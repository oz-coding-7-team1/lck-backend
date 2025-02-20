docker-compose run --rm --entrypoint "\
    certbot certonly \
    -d umdoong.shop \
    -d *.umdoong.shop \
    --email umdoongs@gmail.com \
    --manual --preferred-challenges dns \
    --server https://acme-v02.api.letsencrypt.org/directory \
    --force-renewal" certbot

docker-compose exec app-nginx-1 nginx -s reload