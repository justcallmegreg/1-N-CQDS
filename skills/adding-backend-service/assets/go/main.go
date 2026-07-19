package main

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	cfg, err := LoadConfig()
	if err != nil {
		log.Fatalf("config: %v", err)
	}
	db, err := gorm.Open(postgres.Open(cfg.DatabaseURL), &gorm.Config{})
	if err != nil {
		log.Fatalf("db: %v", err)
	}
	if err := db.AutoMigrate(&itemModel{}); err != nil {
		log.Fatalf("migrate: %v", err)
	}
	repo := NewItemRepository(db)

	r := chi.NewRouter()
	r.Get("/health", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, map[string]string{"status": "ok"})
	})
	r.Get("/health/ready", func(w http.ResponseWriter, _ *http.Request) {
		sqlDB, _ := db.DB()
		if err := sqlDB.Ping(); err != nil {
			http.Error(w, "not ready", http.StatusServiceUnavailable)
			return
		}
		writeJSON(w, map[string]string{"status": "ready"})
	})
	r.Get("/items", func(w http.ResponseWriter, _ *http.Request) {
		items, err := repo.List()
		if err != nil {
			http.Error(w, err.Error(), 500)
			return
		}
		writeJSON(w, items)
	})
	r.Post("/items", func(w http.ResponseWriter, req *http.Request) {
		var body struct{ Name string }
		json.NewDecoder(req.Body).Decode(&body)
		item, err := repo.Add(body.Name)
		if err != nil {
			http.Error(w, err.Error(), 500)
			return
		}
		writeJSON(w, item)
	})
	log.Fatal(http.ListenAndServe(":8000", r))
}

func writeJSON(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(v)
}
