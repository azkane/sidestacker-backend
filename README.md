# Sidestacker backend

This repository is the backend of the sidestacker game.

## How to run

The backend is served using the flask development server as this is only a demo.

It expects the frontend to be compiled and the build directory to be in the root
of this repository.

Assuming the frontend lives in a neighboring folder named `sidestacker-front` and that
a virtualenv has been initialized, the following commands would install dependencies and
start the server:

```shell
pip install -r requirements.txt
SBWD=$(pwd)
cd ../sidestacker-front
yarn && yarn build
cp -rf build/ $SBWD
cd $SBWD
flask run
```

At this point the game would be running on `http://localhost:5000`.

## Play now

The game is currently deployed at https://sidestacker.parenlambda.dev

