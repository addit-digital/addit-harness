# HTTP services with Gin

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: Gin docs (https://gin-gonic.com/docs/), Gin GitHub (https://github.com/gin-gonic/gin), net/http Server.Shutdown (https://pkg.go.dev/net/http#Server.Shutdown), os/signal NotifyContext (https://pkg.go.dev/os/signal#NotifyContext), go-playground/validator (https://pkg.go.dev/github.com/go-playground/validator/v10).

Examples use **Gin**. The same shape works with net/http: a handler is `func(http.ResponseWriter, *http.Request)`, routing via `http.ServeMux` (Go 1.22+ supports method+path patterns), and the graceful-shutdown section below is plain `net/http`.

## Keep handlers thin
- decode → validate → call service → encode. Business logic lives in services, not handlers. Inject dependencies via a handler struct, never globals.
  ```go
  type OrderAPI struct {
      svc *order.Service
      log *slog.Logger
  }
  ```

## Routing & groups
```go
r := gin.New()
r.Use(gin.Recovery(), requestLogger(log))

v1 := r.Group("/v1")
{
    orders := v1.Group("/orders")
    orders.GET("/:id", api.get)
    orders.POST("", api.create)
}
```

## Binding + validation
- Bind and validate in one step with `binding` tags (backed by go-playground/validator). `ShouldBindJSON` returns an error instead of auto-writing 400, so you control the response.
  ```go
  type createReq struct {
      UserID string `json:"user_id" binding:"required"`
      Total  int64  `json:"total"   binding:"required,gt=0"`
      Email  string `json:"email"   binding:"omitempty,email"`
  }

  func (a *OrderAPI) create(c *gin.Context) {
      var req createReq
      if err := c.ShouldBindJSON(&req); err != nil {
          c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
          return
      }
      o, err := a.svc.Create(c.Request.Context(), req.UserID, req.Total)
      if err != nil {
          a.writeErr(c, err)
          return
      }
      c.JSON(http.StatusCreated, o)
  }
  ```
- Use `c.Request.Context()` for downstream calls so client cancellation/timeouts propagate.

## Middleware
- Cross-cutting concerns (logging, recovery, auth, request IDs) are middleware. Put shared values in the context, call `c.Next()`, short-circuit with `c.AbortWithStatus`.
  ```go
  func auth(c *gin.Context) {
      uid, ok := verify(c.GetHeader("Authorization"))
      if !ok { c.AbortWithStatus(http.StatusUnauthorized); return }
      c.Set("uid", uid)
      c.Next()
  }
  ```

## Error handling
- Map domain errors to status codes in one place; never leak internal error strings to clients.
  ```go
  func (a *OrderAPI) writeErr(c *gin.Context, err error) {
      switch {
      case errors.Is(err, order.ErrNotFound):
          c.JSON(http.StatusNotFound, gin.H{"error": "not found"})
      case errors.As(err, new(*order.ValidationError)):
          c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
      default:
          a.log.ErrorContext(c.Request.Context(), "request failed", "err", err)
          c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
      }
  }
  ```

## Graceful shutdown
- Wrap Gin in `http.Server`, cancel the root context on SIGINT/SIGTERM, and drain in-flight requests with a bounded timeout.
  ```go
  ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
  defer stop()

  srv := &http.Server{Addr: cfg.Addr, Handler: r}
  go func() {
      if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
          log.Error("listen", "err", err)
      }
  }()

  <-ctx.Done()
  shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
  defer cancel()
  if err := srv.Shutdown(shutdownCtx); err != nil {
      log.Error("shutdown", "err", err)
  }
  ```
- Set server timeouts (`ReadHeaderTimeout`, `WriteTimeout`) to resist slow-client attacks. Use `gin.New()` + explicit middleware in production over `gin.Default()`, and set `gin.SetMode(gin.ReleaseMode)`.
