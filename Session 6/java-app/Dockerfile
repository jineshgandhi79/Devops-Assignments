FROM openjdk:11-jdk-slim
WORKDIR /app
COPY HelloWorld.java .
RUN javac HelloWorld.java
EXPOSE 8080
CMD ["java", "HelloWorld"]
