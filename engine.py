from pyspark.sql.types import *
from pyspark.sql.functions import explode, col

from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator

from pyspark.sql import SQLContext

import random

class RecommendationEngine:

    """
        Create new User.
    """
    def create_user(self, user_id):
        if user_id == None:
            self.max_user_identifier = self.max_user_identifier + 1
        elif user_id > self.max_user_identifier:
            self.max_user_identifier = user_id
        return self.max_user_identifier

    """
        Check is a user known.
    """
    def is_user_known(self, user_id):
        return user_id != None and user_id <= self.max_user_identifier

    """
        Get a movie.
    """
    def get_movie(self, movie_id):
        if movie_id == None:
            best_movies_struct = [StructField("movieId", IntegerType(), True),
		        StructField("title", StringType(), True),
		        StructField("count", IntegerType(), True)]
            best_movies_df = self.spark.createDataFrame(self.most_rated_movies, StructType(best_movies_struct))
            return best_movies_df.sample(False, fraction=0.05).select("movieId", "title").limit(1)
        else:
            return self.movies_df.filter("movieId == " + str(movie_id))

    """
        Get ratings for user.
    """
    def get_ratings_for_user(self, user_id):
        return self.ratings_df.filter("userId == " + str(user_id))

    """
        Adds new ratings to the model dataset and train the model again.
    """
    def add_ratings(self, user_id, ratings):
        rating_struct = [StructField("movieId", IntegerType(), True),
            StructField("userId", IntegerType(), True),
            StructField("rating", DoubleType(), True)]
        
        ratings_list = list(ratings)
        print("Add {} new ratings to train the model".format(len(ratings_list)))

        new_ratings_df = self.spark.createDataFrame(ratings_list, StructType(rating_struct))
        self.ratings_df = self.ratings_df.union(new_ratings_df)

        # Splitting training data
        self.training, self.test = self.ratings_df.randomSplit([0.8, 0.2], seed=12345)
        self.__train_model()

    """
        Given a user_id and a movie_id, predict ratings for it.
    """
    def predict_rating(self, user_id, movie_id):
        data = [(user_id, movie_id)]

        rating_struct = [StructField("userId", IntegerType(), True),
            StructField("movieId", IntegerType(), True)]
        rating_df = self.spark.createDataFrame(data, StructType(rating_struct))

        prediciton_df = self.model.transform(rating_df)
        if (prediciton_df.count() == 0):
            return -1
        return prediciton_df.collect()[0].asDict()["prediction"]

    """
        Returns the top recommendations for a given user.
    """
    def recommend_for_user(self, user_id, nb_movies):
        user_df = self.spark.createDataFrame([user_id], IntegerType()).withColumnRenamed("value", "userId")
        ratings = self.model.recommendForUserSubset(user_df, nb_movies)
        user_recommandations = ratings.select(
             explode(col("recommendations").movieId).alias("movieId")
        )
        return user_recommandations.join(self.movies_df, "movieId").drop("genres").drop("movieId")

    """
        Train the model with ALS.
    """
    def __train_model(self):
        als = ALS(maxIter=self.max_iter,
                  regParam=self.reg_param, \
                  implicitPrefs=False, \
                  userCol="userId", \
                  itemCol="movieId", \
                  ratingCol="rating", \
                  coldStartStrategy="drop")

        self.model = als.fit(self.training)
        self.__evaluate()

    """
        Evaluate the model by calculating the Root-mean-square error.
    """
    def __evaluate(self):
        predictions = self.model.transform(self.test)
        evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
        self.rmse = evaluator.evaluate(predictions)
        print("Root-mean-square error = " + str(self.rmse))

    """
        Load datasets and train the model.
    """
    def __init__(self, sc, movies_set_path, ratings_set_path):
        self.spark = SQLContext(sc).sparkSession
        
        # Get hyper parameters from command line
        self.max_iter = 9
        self.reg_param = 0.05

        print("MaxIter {}, RegParam {}.".format(self.max_iter, self.reg_param))

        # Define schema for movies dataset
        movies_struct = [StructField("movieId", IntegerType(), True),
            StructField("title", StringType(), True),
            StructField("genres", StringType(), True)]

        movies_schema = StructType(movies_struct)

        # Define schema for ratings dataset
        ratings_struct = [StructField("userId", IntegerType(), True),
        StructField("movieId", IntegerType(), True),
        StructField("rating", DoubleType(), True),
        StructField("timestamp", IntegerType(), True)]

        ratings_schema = StructType(ratings_struct)

        # Read movies from HDFS
        self.movies_df = self.spark.read.format("csv") \
            .option("header", "true") \
            .option("delimiter", ",") \
            .schema(movies_schema) \
            .load(movies_set_path)

        self.movies_count = self.movies_df.count()
        print("Number of movies : {}.".format(self.movies_count))

        # Read ratings from HDFS
        self.ratings_df = self.spark.read.format("csv") \
            .option("header", "true") \
            .option("delimiter", ",") \
            .schema(ratings_schema) \
            .load(ratings_set_path) \
            .drop("timestamp")

        self.max_user_identifier = self.ratings_df.select('userId').distinct().sort(col("userId").desc()).limit(1).take(1)[0].userId
        print("Max user id : {}.".format(self.max_user_identifier))

        self.most_rated_movies = self.movies_df \
            .join(self.ratings_df, "movieId") \
            .groupBy(col("movieId"), col("title")).count().orderBy("count", ascending=False) \
            .limit(200).collect()

        # Splitting training data
        self.training, self.test = self.ratings_df.randomSplit([0.8, 0.2], seed=12345)

        self.__train_model()
