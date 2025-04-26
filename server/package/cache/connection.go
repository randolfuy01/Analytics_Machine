package cache

import (
	"fmt"
	"os"

	"github.com/redis/go-redis/v9"
)

func init_cache() *redis.Client {
	var port string = os.Getenv("port")
	fmt.Printf("Initializing cache on port %s", port)
	client := redis.NewClient(&redis.Options{
		Addr:     port,
		Password: "",
		DB:       0,
		Protocol: 2,
	})
	return client
}

func get_cache_content(client) 
