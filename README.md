
#### Prereqs :

```console
sudo su
```

- Update the OS :

```console
yum update
```

- Clone this Git

```console
yum install git -y
https://github.com/mehdi-lamrani/spark-movie.git
```

- Install java

```console
yum install java -y
```

- Install Spark 3.0

```console
wget https://dlcdn.apache.org/spark/spark-3.3.0/spark-3.3.0-bin-hadoop3.tgz
tar -xvf spark-3.3.0-bin-hadoop3.tgz 
rm -rf spark-3.3.0-bin-hadoop3.tgz 
mv spark-3.3.0-bin-hadoop3/ spark-3.3.0
```

- Set Environment viariables
```console
echo "export SPARK_HOME=/root/spark-3.3.0" > .bashrc
echo "export PATH=$PATH:$SPARK_HOME/bin" > .bashrc
. .bashrc
```

- The CherryPy framework features a reliable, HTTP/1.1-compliant, WSGI thread-pooled webserver.

```console
pip3 install CherryPy
```

- Flask is a micro web framework written in Python.

```console
pip3 install Flask
```

pandas is a data manipulation and analysis library (Cython is necessary for pandas installation).

```console
pip3 install Cython
pip3 install pandas
```

findspark adds pyspark to sys.path at runtime
```console
pip3 install findspark
```

- Exposer you app to the outside world 
```console
sudo sed -i "s/localhost/$(curl http://checkip.amazonaws.com)/g" ./static/index.js
```
:warning: remember to have your personal IP whitelisted on the security group of the EC2 instance (ask trainer/admin)

**Our complete web service contains three Python files:**
* ***engine.py*** defines the recommendation engine, wrapping inside all the Spark related computations.
* ***app.py*** is a Flask web application that defines a RESTful API around the engine.
* ***server.py*** initialises a CherryPy webserver after creating a Spark context and Flask web app.



- To run the app :
```console
spark-submit server.py /root/spark-movies/ml-latest/movies.csv /root/spark-movies/ml-latest/ratings.csv
```
## The application deploys :

### A web page :

Can be accessed on : http://localhost(or-ec2-ip):5432

### Three rest services :

#### Getting Top Recommendations :

Here we call the service to get the top 10 recommendations for the user 331 :
```console
curl -H "Accept: application/json; Content-Type: application/json" -X GET http://localhost:5432/331/ratings/top/10 | python -m json.tool
```

#### Getting Individual Ratings :

Here we call the to get the predicted rating for the movie The Quiz (1994) for the user 12 :
```console
curl -H "Content-Type: application/json" -X GET http://localhost:5432/12/ratings/858
```

#### Adding New Ratings

Add new ratings for a specific user and recompute the prediction model for every new batch of user ratings.
Here we call the service for the user 331 :
```console
curl -H "Accept: text/csv; Content-Type: application/json" -X POST http://localhost:5432/331/ratings -F 'file=@ml-latest/new-ratings.csv'
```

The format is a series of lines (ending with the newline separator) with movie_id and rating separated by commas. For example, the following file corresponds to the ten new user ratings used as a example in the tutorial about building the model:
```csv
260,4.6  
1,4
16,3.5  
25,4  
32,5 
335,4
379,3
296,1
858,1
50,2.3
```
