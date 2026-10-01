# Go: data access

Scope: MongoDB v2, SQL, ids and money. Signals: `mongo.`, `bson.`, `database/sql`, `uuid.`, `decimal.`. DATA-2 is overridable by id (a SQL repo overrides it).

- **G-DATA-1** Call the driver only with a `ctx` (`FindOne(ctx, ...)`, `QueryContext`), never the context-free variants. Src: [go.dev manage connections](https://go.dev/doc/database/manage-connections)
  Why: cancellation and deadlines reach the database.
- **G-DATA-2** MongoDB: the v2 driver (`go.mongodb.org/mongo-driver/v2`); soft delete (`active: false`), never hard delete; `FindOneAndUpdate` with `ReturnDocument(After)`; `snake_case` bson names; collection names as package constants; detect not-found with `errors.Is(err, mongo.ErrNoDocuments)`. Src: owner
  Why: one set of data rules across repositories.
- **G-DATA-3** SQL: set `SetMaxOpenConns` and `SetConnMaxLifetime` on the `*sql.DB`, and always close rows (`defer rows.Close()`). Src: [go.dev manage connections](https://go.dev/doc/database/manage-connections)
  Why: the pool is unbounded by default and unclosed rows keep a connection busy.
- **G-DATA-4** Ids are `uuid.UUID`, never bare `string`; money and quantities are a decimal type (G-4). Src: owner
  Why: the type rejects malformed ids and float rounding.

```go
res := coll.FindOneAndUpdate(ctx,
	bson.M{"_id": id, "active": true},
	bson.M{"$set": update},
	options.FindOneAndUpdate().SetReturnDocument(options.After))
```
