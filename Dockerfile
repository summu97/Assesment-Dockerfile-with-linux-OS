FROM ubuntu AS build-stage

# Install required packages and clean up
RUN apt-get update && \
    apt-get install -y \
    openjdk-11-jdk \
    git \
    curl \
    gzip \
    tar \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Apache Maven 3.x
ENV MAVEN_VERSION=3.9.5
ENV M2_HOME=/opt/apache-maven-${MAVEN_VERSION}
ENV PATH="${M2_HOME}/bin:${PATH}"

RUN mkdir -p ${M2_HOME} && \
    curl -fsSL "https://downloads.apache.org/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz" | tar -xzC ${M2_HOME} --strip-components=1

RUN git clone https://github.com/SaravanaNani/jenkins-java-project.git /maven

WORKDIR /maven

RUN mvn clean package

FROM ubuntu:latest

# Installing Java latest version
RUN apt-get update && \
    apt-get install -y \
    openjdk-17-jdk 

# Set environment variables for Java
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV PATH=$JAVA_HOME/bin:$PATH

# Install Python3
RUN apt-get install -y python-is-python3 \
    python3-pip

# Set environment variables for Python
ENV PYTHON_HOME=/usr/bin/python3
ENV PATH=$PYTHON_HOME:$PATH

# Download and extract Apache Tomcat
ADD https://dlcdn.apache.org/tomcat/tomcat-11/v11.0.0/bin/apache-tomcat-11.0.0.tar.gz .
RUN tar -zxvf apache-tomcat-11.0.0.tar.gz && \
    rm apache-tomcat-11.0.0.tar.gz

# Configure Tomcat users
RUN sed -i '56 a\<role rolename="manager-gui"/>' apache-tomcat-11.0.0/conf/tomcat-users.xml && \
    sed -i '57 a\<role rolename="manager-script"/>' apache-tomcat-11.0.0/conf/tomcat-users.xml && \
    sed -i '58 a\<user username="tomcat" password="tomcat" roles="manager-gui, manager-script"/>' apache-tomcat-11.0.0/conf/tomcat-users.xml && \
    sed -i '59 a\</tomcat-users>' apache-tomcat-11.0.0/conf/tomcat-users.xml && \
    sed -i '56d' apache-tomcat-11.0.0/conf/tomcat-users.xml && \
    sed -i '21d' apache-tomcat-11.0.0/webapps/manager/META-INF/context.xml && \
    sed -i '22d' apache-tomcat-11.0.0/webapps/manager/META-INF/context.xml

COPY --from=build-stage /maven/target/*.war ./apache-tomcat-11.0.0/webapps

RUN mv ./apache-tomcat-11.0.0 /usr/local/

# Install apache2
RUN apt-get update -y
RUN apt-get install apache2 -y
COPY ./index.html /var/www/html

EXPOSE 80
EXPOSE 8080

# CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]
# ENTRYPOINT ["/usr/local/apache-tomcat-11.0.0/bin/catalina.sh", "run"]
CMD ["sh", "-c", "/usr/sbin/apachectl -D FOREGROUND & /usr/local/apache-tomcat-11.0.0/bin/catalina.sh run"]
