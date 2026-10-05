terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_network" "app_network" {
  name = "task-tracker-prod"
}

resource "docker_image" "app" {
  name = "task-tracker:latest"
}

resource "docker_container" "db" {
  image = "postgres:16"
  name  = "task-tracker-prod-db"

  env = [
    "POSTGRES_USER=postgres",
    "POSTGRES_PASSWORD=postgres",
    "POSTGRES_DB=tasktracker"
  ]

  networks_advanced {
    name = docker_network.app_network.name
  }

  volumes {
    volume_name = "task-tracker-prod-pgdata"
    container_path = "/var/lib/postgresql/data"
  }
}

resource "docker_container" "app" {
  name = "task-tracker"
  image = docker_image.app.image_id

  ports {
    internal = 8000
    external = 8001
  }

  env = [
      "DATABASE_URL=postgresql+psycopg2://postgres:postgres@task-tracker-prod-db:5432/tasktracker"
  ]

  networks_advanced {
    name = docker_network.app_network.name
  }

  depends_on = [docker_container.db]
}