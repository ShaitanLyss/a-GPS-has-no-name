# a-GPS-has-no-name
Une armade de microservices pour un tracking GPS nouvelle génération.

## Configuration
- copier .env.example et le nommer .env
- modifier les variables d'environnement dans le fichier .env

## Vous lancer tout
docker-compose up -d

## quelques tests

docker-compose logs consumer

docker-compose logs producer_1

docker-compose logs producer_2

## Test de fastapi

## recuperer l'ip du container (container_pi)
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fastapi

## tester les routes ( 2 routes pour l'instant)
# ici '9c02361d9ed5' = champ name que vous verrez afficher dans les logs d'un producteur, 
# ici '9c02361d9' est à remplacer par ce que vous aurez chez vous

curl -X GET "http://container_pi:8000/location/9c02361d9ed5" -H "accept: application/json"


curl -X GET "http://container_pi:8000/location/tout/9c02361d9ed5" -H "accept: application/json"


