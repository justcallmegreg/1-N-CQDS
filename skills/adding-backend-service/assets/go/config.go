package main

import (
	"os"
	"strings"
)

type Config struct {
	DatabaseURL string
	ServiceName string
}

func LoadConfig() (Config, error) {
	url := os.Getenv("DATABASE_URL")
	if url == "" {
		return Config{}, os.ErrInvalid
	}
	name := os.Getenv("SERVICE_NAME")
	if name == "" {
		name = "service"
	}
	return Config{DatabaseURL: normalizeDSN(url), ServiceName: name}, nil
}

// normalizeDSN strips SQLAlchemy-style "+driver" scheme suffixes
// (e.g. "postgresql+psycopg://...") down to the plain scheme
// ("postgresql://...") that pgx/GORM accepts. This lets the same
// DATABASE_URL documented for the Python skeleton — which uses
// SQLAlchemy's dialect+driver:// form — also work unmodified for the
// Go skeleton, whose pgx driver rejects the "+driver" suffix outright.
// Plain postgres:// / postgresql:// URLs and keyword DSNs (host=...)
// pass through unchanged.
func normalizeDSN(url string) string {
	if i := strings.Index(url, "://"); i > 0 {
		scheme := url[:i]
		if p := strings.Index(scheme, "+"); p >= 0 {
			return scheme[:p] + url[i:]
		}
	}
	return url
}
