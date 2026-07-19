package main

import (
	"os"
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
	return Config{DatabaseURL: url, ServiceName: name}, nil
}
