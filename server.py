import time, sys, cherrypy, os

from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher

from app import create_app

from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession

# load spark context

from app import create_app
import cherrypy

conf = SparkConf().setAppName("movie_recommendation-server")
# IMPORTANT: pass aditional Python modules to each worker
# Init spark context and load libraries
sc = SparkContext(conf=conf, pyFiles=['engine.py', 'app.py'])

# Get the paths to the movies and ratings dataset
movies_set_path = sys.argv[1] if len(sys.argv) > 1 else ""
ratings_set_path = sys.argv[2] if len(sys.argv) > 2 else ""
    

app = create_app(sc, movies_set_path, ratings_set_path)

cherrypy.tree.graft(app.wsgi_app, '/')
cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 5432,
                        'engine.autoreload.on': False
                        })

if __name__ == '__main__':
    cherrypy.engine.start()