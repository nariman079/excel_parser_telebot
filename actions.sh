#!/bin/bash

#Проверка на передачи 2ух аргументов
if [ "$#" -ne 2 ]; then
  echo "Использование: ./action.sh <environment> <action>"
  echo "Пример: ./action.sh prod run"
  exit 1
fi

#Arguments
ENVIRONMENT=$1
ACTION=$2


#Check environment argument
case $ENVIRONMENT in
  prod)
    echo "Среда: PROD"
    # В зависимости от второго аргумента выполняем действие
    case $ACTION in
      run)
        echo "Запуск в PROD среде..."
        # Здесь код для запуска в продакшн среде
        # Например, можно выполнить команду деплоя
        # docker-compose -f docker-compose.prod.yml up -d
        ;;
      down)
        echo "Остановка в PROD среде..."
        # Здесь код для остановки в продакшн среде
        # Например, можно выполнить команду остановки
        # docker-compose -f docker-compose.prod.yml down
        ;;
      *)
        echo "Неизвестное действие: $ACTION. Доступные действия для PROD: run, down"
        exit 1
        ;;
    esac
    ;;
  local)
    echo "Среда: LOCAL"
    # В зависимости от второго аргумента выполняем действие
    case $ACTION in
      run)
        echo "Запуск в LOCAL среде..."
        docker compose -f database.local.yaml -f docker-compose.local.yaml up
        ;;
      build)
        echo "Запуск в LOCAL среде..."
        docker compose -f database.local.yaml -f docker-compose.local.yaml up --build
        ;;
      down)
        echo "Остановка в LOCAL среде..."
        # Здесь код для остановки в продакшн среде
        # Например, можно выполнить команду остановки
        docker compose -f database.local.yaml -f docker-compose.local.yaml down
        ;;
      *)
        echo "Неизвестное действие: $ACTION. Доступные действия для PROD: run, down"
        exit 1
        ;;
    esac
    ;;
  *)
    echo "Неизвестная среда: $ENVIRONMENT. Доступные среды: prod"
    exit 1
    ;;
esac
