# WeatherWatch
raspbery pi weather data collector

## BOM

## python libs
- [pipdeptree](https://pypi.org/project/pipdeptree/)
- [coverage](https://pypi.org/project/coverage/)
- [black](https://pypi.org/project/black/)
- [RPi.gpio](https://pypi.org/project/RPi.GPIO/)

## tests
 p3 setup.py test -v  -s <fully qualified test class>

## build system
- [jenkins](https://www.jenkins.io/)
    - [docker container](https://github.com/jenkinsci/docker/)
    - [credentials plugin](https://github.com/jenkinsci/credentials-plugin)
    - [ssh agent plugin](https://plugins.jenkins.io/ssh-agent/)
    - [sonarqube scanner plugin](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner-for-jenkins/)
- [remote agent on PI](https://www.gdcorner.com/2019/12/27/JenkinsHomeLab-P2-LinuxAgents.html)
    - [added known_host to docker data](https://stackoverflow.com/questions/44441935/cant-connect-to-jenkins-slave-no-known-hosts-file-was-found-at-var-jenkins-hom)
    - gen ssh key via [putty](https://www.ssh.com/academy/ssh/putty/windows/puttygen)
    - for jenkins ssh key creds need to export private key as [openssh format](https://stackoverflow.com/questions/53636532/jenkins-what-is-the-correct-format-for-private-key-in-credentials) 
    - add jenkins to needed [groups](https://forums.raspberrypi.com/viewtopic.php?t=225274)
    
## TODOs    
