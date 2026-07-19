# Multi-arch build. Static binary, distroless-nonroot runtime, pinned digests.
# Digests below are examples — immutable so they never fail, but they go
# stale (CVE drift) over time; the skill re-pins to current at build,
# same as the Python Dockerfile.
FROM golang@sha256:60deed95d3888cc5e4d9ff8a10c54e5edc008c6ae3fba6187be6fb592e19e8c0 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/service ./...

FROM gcr.io/distroless/static-debian12@sha256:aef9602f8710ec12bde19d593fed1f76c708531bb7aba205110f1029786ead7b
COPY --from=build /out/service /service
USER nonroot:nonroot
EXPOSE 8000
ENTRYPOINT ["/service"]
