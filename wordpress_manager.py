#!/usr/bin/env python3
import os
import subprocess
import sys

def check_install_docker():
    if subprocess.call(["docker", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        print("Docker is not installed. Installing Docker...")
        subprocess.run(["sudo", "apt-get", "update"])
        subprocess.run(["sudo", "apt-get", "install", "-y", "docker.io"])
        subprocess.run(["sudo", "systemctl", "start", "docker"])
        subprocess.run(["sudo", "systemctl", "enable", "docker"])
        print("Docker installed and started.")
    else:
        print("Docker is already installed.")

def check_install_docker_compose():
    if subprocess.call(["docker-compose", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        print("Docker Compose is not installed. Installing Docker Compose...")
        subprocess.run(["sudo", "curl", "-L", "-o", "/usr/local/bin/docker-compose", "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)"])
        subprocess.run(["sudo", "chmod", "+x", "/usr/local/bin/docker-compose"])
        print("Docker Compose installed.")
    else:
        print("Docker Compose is already installed.")

def create_wordpress_site(site_name):
    check_install_docker()
    check_install_docker_compose()

    os.makedirs(site_name)
    os.chdir(site_name)

    with open("docker-compose.yml", "w") as f:
        f.write(f"""version: '3'
services:
  wordpress:
    image: wordpress:latest
    ports:
      -  '8080:80'
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - ./wp-content:/var/www/html/wp-content
  db:
    image: mariadb:latest
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress
    volumes:
      - db_data:/var/lib/mysql
volumes:
  db_data:
""")

    os.mkdir("wp-content")
    with open("/etc/hosts", "a") as f:
        f.write(f"127.0.0.1 {site_name}\n")

    print(f"Site '{site_name}' created. Open http://{site_name} in your browser.")

# Add functions for enable, disable, and delete subcommands here
def enable_disable_site(site_name, enable):
    action = "up" if enable else "down"
    subprocess.run(["docker-compose", action, "-d"], cwd=site_name)
    status = "enabled" if enable else "disabled"
    print(f"Site '{site_name}' {status}. Open http://{site_name} in your browser.")

def delete_site(site_name):
    subprocess.run(["docker-compose", "down"], cwd=site_name)
    os.chdir("..")
    subprocess.run(["rm", "-rf", site_name])
    with open("/etc/hosts", "r") as f:
        lines = f.readlines()
    with open("/etc/hosts", "w") as f:
        for line in lines:
            if not line.startswith(f"127.0.0.1 {site_name}"):
                f.write(line)
    print(f"Site '{site_name}' deleted.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <site_name> <command>")
        sys.exit(1)

    site_name = sys.argv[1]
    command = sys.argv[2]

    if command == "create":
        create_wordpress_site(site_name)
    elif command == "enable":
        enable_disable_site(site_name, enable=True)
    elif command == "disable":
        enable_disable_site(site_name, enable=False)
    elif command == "delete":
        delete_site(site_name)
    else:
        print("Unknown command.")

