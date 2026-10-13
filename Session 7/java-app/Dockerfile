FROM openjdk:11-jdk-slim
WORKDIR /app
COPY Main.java .
RUN javac Main.java
EXPOSE 8081
CMD ["java", "Main"]
