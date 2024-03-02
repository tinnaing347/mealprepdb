#!/bin/bash 
set -e

usage_exit(){
    printf '\nUsage: %s: [-n] name [-m] marker \n' $0; exit 1;
}



marker=""
name=""
nameset=0
markerset=0

while getopts n:m:h flag; do 
    case "${flag}" in 
        m) marker=${OPTARG}; markerset=1;; 
        n) name=${OPTARG}; nameset=1;;        
        ?|h) usage_exit
    esac 
done 

POSTGRES_USER="${MEALPREPDB_POSTGRES_USER}"
POSTGRES_PASSWORD="${MEALPREPDB_POSTGRES_PASSWORD}"
POSTGRES_TEST_DB="${MEALPREPDB_POSTGRES_TEST_DB}"
POSTGRES_HOST="${MEALPREPDB_POSTGRES_HOST}" 
POSTGRES_PORT="${MEALPREPDB_POSTGRES_PORT}"


if [[ -v $POSTGRES_USER || -v $POSTGRES_PASSWORD || -v $POSTGRES_TEST_DB || -v $POSTGRES_HOST || -v $POSTGRES_PORT ]]; then 
    
    echo "POSTGRES Environment variables not configured."; 
    echo POSTGRES_USER: $POSTGRES_USER
    echo POSTGRES_PASSWORD: $POSTGRES_PASSWORD
    echo POSTGRES_TEST_DB: $POSTGRES_TEST_DB
    echo POSTGRES_HOST: $POSTGRES_HOST
    echo POSTGRES_PORT: $POSTGRES_PORT
    
    exit 1;
fi


PGPASSWORD=${POSTGRES_PASSWORD} dropdb -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -U ${POSTGRES_USER} -e -f --if-exists ${POSTGRES_TEST_DB}
PGPASSWORD=${POSTGRES_PASSWORD} createdb -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -U ${POSTGRES_USER} -e ${POSTGRES_TEST_DB}


poetry run alembic upgrade head

# if we get a module name the run that one, or a marker name run that one or run everything
# if both -n and -m are set then -n takes precedence.
if [ $nameset -eq 1 ] 
then
    poetry run pytest --cov=mealprepdb/ --cov-report=term-missing ${name} -v -s
    
elif [ $markerset -eq 1 ]
then  
    poetry run pytest -v -s -m ${marker} --cov=mealprepdb/ --cov-report=term-missing 

else 
    poetry run pytest -s -v -m "not live" --cov=mealprepdb/ --cov-report=term-missing

fi
poetry run alembic downgrade base
poetry run mypy mealprepdb/api --strict

PGPASSWORD=${POSTGRES_PASSWORD} dropdb -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -U ${POSTGRES_USER} -e -f --if-exists ${POSTGRES_TEST_DB}