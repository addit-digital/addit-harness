# JSON, struct tags & serialization

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: encoding/json package (https://pkg.go.dev/encoding/json), JSON and Go / Go blog (https://go.dev/blog/json), Uber Go Style Guide — struct tags (https://github.com/uber-go/guide/blob/master/style.md).

## Tags
- Always set explicit `json` tags on marshaled structs — don't rely on field-name defaults, which change if you rename a field.
  ```go
  type Order struct {
      ID        string    `json:"id"`
      Total     int64     `json:"total"`
      Note      string    `json:"note,omitempty"`
      Internal  string    `json:"-"`            // never marshaled
      CreatedAt time.Time `json:"created_at"`
  }
  ```
- Only **exported** (capitalized) fields are marshaled. `-` skips a field entirely.

## omitempty pitfalls
- `omitempty` drops the field when it holds the type's zero value — but `0`, `false`, and `""` are valid zero values you often *do* want to send. `omitempty` can't tell "unset" from "set to zero".
- For genuinely optional/nullable scalars, use a pointer so `nil` means "absent" and `*v` carries the real value:
  ```go
  type Patch struct {
      Active *bool `json:"active,omitempty"` // nil = unchanged, &false = set to false
  }
  ```

## Custom marshaling
- Implement `MarshalJSON`/`UnmarshalJSON` for non-default wire formats (enums as strings, custom timestamps):
  ```go
  func (s Status) MarshalJSON() ([]byte, error) {
      return json.Marshal(s.String())
  }
  ```
- Use `json.Number` (with `Decoder.UseNumber()`) to preserve large/precise numbers that would lose precision as `float64`.

## time.Time
- Marshals/unmarshals as RFC 3339 (`2006-01-02T15:04:05Z07:00`). Store and transmit UTC.

## Decoding untrusted input
- Validate after decoding — JSON decoding does not enforce your invariants; missing fields silently become zero values.
- Reject unexpected fields when strictness matters:
  ```go
  dec := json.NewDecoder(r.Body)
  dec.DisallowUnknownFields()
  if err := dec.Decode(&req); err != nil { ... }
  ```
- Stream large payloads with `json.Decoder`/`json.Encoder` instead of buffering whole documents with `Marshal`/`Unmarshal`.
- In Gin, `c.ShouldBindJSON` plus `binding` tags handles decode + validation in one step (see http-gin.md).
