# Go: HTTP handlers and routes

Scope: Gin handlers, routes, validation, error rendering. Signals: `gin.`, `http.Handler`, `ShouldBindJSON`, router groups. HTTP-1, 2, 4, 6 are overridable by id (net/http and other frameworks can comply).

- **G-HTTP-1** Mount routes under a versioned prefix `/api/v{n}/<resource>` (default; overridable) and apply authentication middleware at the group level, tightening per route. Src: owner
  Why: one group-level auth line cannot be forgotten on a new route.
- **G-HTTP-2** Verbs: `POST` create, `GET` read, `PUT` replace, `PATCH` partial update, `DELETE` deactivate; `201` for create, `200` otherwise. Lists: `GET` with query params is fine; `POST /list` with a body filter is one example style, never enforced. Src: owner
  Why: a fixed map keeps clients predictable.
- **G-HTTP-3** Handler flow: bind, validate (validator v10 tags) right after binding, call one service method, map the result (G-3). Parse path ids with `uuid.Parse`. Src: owner
  Why: handlers stay thin and a bad request never reaches the service.
- **G-HTTP-4** Handlers never write error statuses; they `_ = c.Error(err); return` and one middleware renders the typed error. Src: owner
  Why: one place maps errors to responses (G-ERR-1).
- **G-HTTP-5** Servers and clients set timeouts (G-7); use `http.Server{ReadHeaderTimeout, ...}`, not `http.ListenAndServe`. Src: [Cloudflare timeouts guide](https://blog.cloudflare.com/the-complete-guide-to-golang-net-http-timeouts/)
  Why: the guide calls the package-level helpers unfit for public servers because their timeouts are off.
- **G-HTTP-6** Without Gin, use Go 1.22 `ServeMux` patterns (`mux.HandleFunc("GET /items/{id}", h)`). Src: [Go routing blog](https://go.dev/blog/routing-enhancements)
  Why: method and wildcard matching are built in.

```go
func (h *handler) handleCreateThing(c *gin.Context) {
	var req CreateThingRequest
	if err := c.ShouldBindJSON(&req); err != nil { _ = c.Error(err); return }
	if err := validator.ValidateRequest(req); err != nil { _ = c.Error(err); return }
	res, err := h.Things.Create(c.Request.Context(), req)
	if err != nil { _ = c.Error(err); return }
	c.JSON(201, res)
}
```
