spark-submit \
    --master spark://spark-master:7077 \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
    jobs/$1


    # --packages org.apache.hadoop:hadoop-aws:3.3.1, \
    #     com.amazonaws:aws-java-sdk:1.11.469, \
    #     org.postgresql:postgresql:42.7.1, \
    #     org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \

# sh jobs/submit.sh votes_streaming.py