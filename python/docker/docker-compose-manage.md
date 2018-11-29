## Descriptions

The `docker-compose` setup and the `manage` script in this folder provides an easy way to run and test the Python Agent. The code is live mounted in Docker so there is the possiblity of supporting live reload while running the container. Cleaning up, rebuilding and restarting the environment is fast - within seconds - so even using a restart model the edit/build/test cycle is fast. 

## Prerequisites
1. [Docker](https://docs.docker.com/install/#supported-platforms)
2. [Git](https://git-scm.com/downloads)
3. A Bash shell.  Bash is standard for Mac and Linux. For Windows, when you installed git from the downloads link above, you will also have installed git-bash. Use it.

## Manage Script

The repo includes the executable `manage` script to control the basic docker-compose commands you will need to use. Use it to do the following from the repo root directory:

- Build the containers: `./manage build`
  - To force a full rebuild: `./manage rebuild`
- Run the Indy ledger, a ledger browser web server and 2 agents: `./manage start`
- Stop the ledger - ctrl-c from where you started it, or `./manage stop` from another terminal session
- Remove persistent storage/reset the environment - `./manage rm`

Note that this is all covered in the `./manage` script usage. Run it with no parameters to see the parameters.

## Running the Agents

- Build the containers - `./manage build`
- Start the indy ledger (and ledger browser app) and agents - `./manage start`
    - access the Agents at [http://localhost:3000](http://localhost:3000) and [http://localhost:3001](http://localhost:3001)
        - The IPs for the agents are `173.17.0.150` and `173.17.0.151`, respectively
    - access the Ledger Browser Web Server at [http://localhost:9000](http://localhost:9000)
- Edit the repo to update files in the running Agents.
- You can shell into an Agent by goint to a separate terminal session (same directory) and running `./manage bash`
    - The repo root folder is live mounted as the  `/indy/home/python` folder
    - Currently, you can update it on the host file system, but not within the docker container (permissions)

## Docker Setup

- The nodes and agents are built based on the `von-image` docker images on [Docker Hub](https://hub.docker.com/r/bcgovimages/von-image/). Look at the two dockerfiles (`pool.dockerfile` and `agent.dockerfile`) to see what von-image tag is being used, and hence, what versions of indy-node and indy-sdk. A table on the von-image Docker Hub page shows the tag-version correspondence.
- The `docker-compose.yml` file starts the four nodes, the ledger browser and the two agents.
- The repo root directory is live mounted in the agent containers as the `/home/indy/python` folder.