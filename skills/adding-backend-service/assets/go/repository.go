package main

import (
	"errors"

	"gorm.io/gorm"
)

// itemModel is the GORM model — internal to the repository.
type itemModel struct {
	ID   uint `gorm:"primaryKey"`
	Name string
}

func (itemModel) TableName() string { return "items" }

// Item is the boundary type — what callers see. No GORM types leak out.
// JSON tags match the Python skeleton's wire shape (lowercase field
// names), so the two Tier-1 services are wire-compatible.
type Item struct {
	ID   uint   `json:"id"`
	Name string `json:"name"`
}

// ErrItemNotFound mirrors Python's get(id) -> Item | None boundary:
// callers get a typed "not found" signal instead of a GORM error type.
var ErrItemNotFound = errors.New("item not found")

type ItemRepository struct{ db *gorm.DB }

func NewItemRepository(db *gorm.DB) *ItemRepository { return &ItemRepository{db: db} }

func (r *ItemRepository) Add(name string) (Item, error) {
	m := itemModel{Name: name}
	if err := r.db.Create(&m).Error; err != nil {
		return Item{}, err
	}
	return Item{ID: m.ID, Name: m.Name}, nil
}

func (r *ItemRepository) Get(id uint) (Item, error) {
	var m itemModel
	if err := r.db.First(&m, id).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return Item{}, ErrItemNotFound
		}
		return Item{}, err
	}
	return Item{ID: m.ID, Name: m.Name}, nil
}

func (r *ItemRepository) List() ([]Item, error) {
	var ms []itemModel
	if err := r.db.Order("id").Find(&ms).Error; err != nil {
		return nil, err
	}
	out := make([]Item, len(ms))
	for i, m := range ms {
		out[i] = Item{ID: m.ID, Name: m.Name}
	}
	return out, nil
}
