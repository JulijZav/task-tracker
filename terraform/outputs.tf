output "app_url" {
  value = "https://localhost:${docker_container.app.ports[0].external}"
}