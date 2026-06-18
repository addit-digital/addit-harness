# Persistence: MongoDB & database/sql

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: mongo-go-driver (https://www.mongodb.com/docs/drivers/go/current/), mongo-driver pkg (https://pkg.go.dev/go.mongodb.org/mongo-driver/mongo), database/sql (https://pkg.go.dev/database/sql), Accessing databases / Go (https://go.dev/doc/database/).

Primary store is **MongoDB** via the official `go.mongodb.org/mongo-driver`; **database/sql** covers the future SQL path. Both follow the same rules: one long-lived pooled handle, always pass `context`, never concatenate untrusted input into queries.

## MongoDB (mongo-go-driver)

### Client & pool
- Create one `*mongo.Client` for the process lifetime and share it; the driver pools connections internally. Disconnect on shutdown.
  ```go
  cli, err := mongo.Connect(ctx, options.Client().
      ApplyURI(cfg.MongoURI).
      SetMaxPoolSize(100).
      SetServerSelectionTimeout(5*time.Second))
  if err != nil { return err }
  defer cli.Disconnect(context.Background())

  coll := cli.Database("shop").Collection("orders")
  ```
- Pass `ctx` (with a deadline) to every operation so calls are cancellable.

### BSON tags & models
```go
type Order struct {
    ID     primitive.ObjectID `bson:"_id,omitempty"`
    UserID string             `bson:"user_id"`
    Total  int64              `bson:"total"`
    Note   string             `bson:"note,omitempty"`
}
```
- Tag every field; `_id,omitempty` lets the server generate the ObjectID on insert.

### CRUD, filters & projections
```go
filter := bson.M{"user_id": uid, "total": bson.M{"$gte": 100}}
opts := options.Find().
    SetProjection(bson.M{"note": 0}).        // exclude field
    SetSort(bson.D{{Key: "total", Value: -1}}).
    SetLimit(20)

cur, err := coll.Find(ctx, filter, opts)
if err != nil { return nil, err }
defer cur.Close(ctx)

var orders []Order
if err := cur.All(ctx, &orders); err != nil { return nil, err }
```
- Single doc: `coll.FindOne(ctx, filter).Decode(&o)`; check `errors.Is(err, mongo.ErrNoDocuments)` for "not found".
- Prefer `bson.D` (ordered) for commands/sorts where order matters; `bson.M` (map) for plain equality filters.

### Transactions / sessions
- Multi-document atomicity needs a session (replica set / sharded cluster). Use `WithTransaction`, which handles retries:
  ```go
  sess, err := cli.StartSession()
  if err != nil { return err }
  defer sess.EndSession(ctx)

  _, err = sess.WithTransaction(ctx, func(sc mongo.SessionContext) (any, error) {
      if _, err := coll.InsertOne(sc, o); err != nil { return nil, err }
      return nil, ledger.InsertOne(sc, entry)
  })
  ```

### Indexes
- Create indexes explicitly at startup to match your query patterns; unindexed filters do collection scans.
  ```go
  _, err = coll.Indexes().CreateOne(ctx, mongo.IndexModel{
      Keys: bson.D{{Key: "user_id", Value: 1}, {Key: "total", Value: -1}},
  })
  ```

## database/sql (SQL future)

### Pool
- `sql.DB` is a pool, not a connection — open once, share for the app lifetime, `Close()` on shutdown. Tune it:
  ```go
  db.SetMaxOpenConns(25)
  db.SetMaxIdleConns(25)
  db.SetConnMaxLifetime(5 * time.Minute)
  ```

### Queries — always Context + parameters
```go
row := db.QueryRowContext(ctx,
    `SELECT id, total FROM orders WHERE user_id = $1`, uid)  // never fmt.Sprintf the value in
var o Order
if err := row.Scan(&o.ID, &o.Total); err != nil { return err }
```
- Use the `...Context` methods (`QueryContext`, `ExecContext`, `QueryRowContext`) everywhere.
- Parameterize with placeholders — never string-concatenate user input (SQL injection).
- For multi-row queries, close and check error:
  ```go
  rows, err := db.QueryContext(ctx, q, args...)
  if err != nil { return err }
  defer rows.Close()
  for rows.Next() { rows.Scan(...) }
  return rows.Err()        // don't forget: Next() hides iteration errors
  ```

### Transactions
```go
tx, err := db.BeginTx(ctx, nil)
if err != nil { return err }
defer tx.Rollback()          // no-op after a successful Commit
if _, err := tx.ExecContext(ctx, q1, ...); err != nil { return err }
return tx.Commit()
```

### Nullable columns
- Use `sql.NullString`/`sql.NullInt64`/... (or pointers) for columns that can be NULL; scanning NULL into a plain `string` errors.

## Migrations
- Manage schema changes with a dedicated tool — `golang-migrate` or `pressly/goose` for SQL; for MongoDB, version index/shape changes with a small migration step at startup. Pick one and keep migrations versioned and immutable once applied.
