# WeatherWatch
raspbery pi weather data collector using OTS parts.

## BOM
- [Nooelec RTL-SDR v5](https://www.nooelec.com/store/nesdr-smart-sdr.html?srsltid=AfmBOooo6Krrq7dvl4eQHVzfA-Yd0QMADqy0cH9XJ5qf-dx8T5dQAby2)
- [indoor Thermo-Hygrometer](https://www.sainlogic.com/english/additional-temperature-and-humidity-sensor-for-sainlogic-weather-station-ft0300.html)
- [outdoor sensor](https://www.sainlogic.com/english/transmitter-for-sainlogic-weather-station-ft0310-1.html)

## libs
- [rtl_433](https://github.com/merbanan/rtl_433)

## python libs
- [pipdeptree](https://pypi.org/project/pipdeptree/)
- [coverage](https://pypi.org/project/coverage/)
- [black](https://pypi.org/project/black/)
- [RPi.gpio](https://pypi.org/project/RPi.GPIO/)

## tests
 python3 setup.py test -v  -s <fully qualified test class>

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

## faq
    - [logging config file](https://gist.github.com/panamantis/5797dda98b1fa6fab2f739a7aacc5e9d)

## TODOs    
