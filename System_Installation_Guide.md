# Installation on Amazon Web Services EC2 #
> ## Install on AMI: ami-4b4ba522 for US East ##

### Step 1: Installing from the Ubuntu Repo ###

Make sure your system is up to date before running the following install commands by running apt-get update & apt-get upgrade.

```
sudo apt-get install htop checkinstall hardinfo sysstat language-pack-gnome-en / 
language-pack-gnome-en-base xorg xorg-docs xterm xserver-xorg x11-apps x11-session-utils /
 x11-utils libx11-dev x11proto-bigreqs-dev x11proto-core-dev x11proto-damage-dev / 
x11proto-dmx-dev x11proto-fixes-dev x11proto-fonts-dev x11proto-gl-dev x11proto-input-dev /
 x11proto-kb-dev x11proto-randr-dev x11proto-record-dev x11proto-render-dev / 
x11proto-resource-dev x11proto-video-dev x11proto-xcmisc-dev x11proto-xext-dev / 
x11proto-xf86bigfont-dev x11proto-xf86dga-dev x11proto-xf86dri-dev / 
x11proto-xf86misc-dev x11proto-xf86vidmode-dev x11proto-xinerama-dev x11-xfs-utils / 
x11-xkb-utils x11-xserver-utils whois apachetop apache2 apache2-mpm-prefork apache2-doc / 
apache2-prefork-dev apache2-utils apache2.2-common idle-python2.6 python-clientform / 
python-crypto python-dbg python-docutils python-doc python-mechanize python-numpy / 
python-numpy-doc python-numpy-dbg python-psycopg2 python-psycopg2-dbg python-pydot / 
python-pyparsing python-roman python-setuptools python-tk python-twisted-conch / 
python-twisted-web2 python-tz python2.6-dbg python2.6-dev python2.6-doc automake1.9 / 
automake1.9-doc g++ g++ g++-multilib fail2ban flex flex-doc clex ml-lex / 
python-gtkglext1 bison bison-doc bisonc++ bisonc++-doc gcc-4.4 gcc-4.4-doc / 
gcc-4.4-locales gcc-4.4-multilib gcc-4.4-source libgcc1-dbg libsoci-core-gcc / 
libsoci-core-gcc-dbg libsoci-core-gcc-dev libsoci-postgresql-gcc gparted java-common / 
gcj-jre gcj-jre-headless cmake icmake make-doc mmake munin-node optipng p7zip-full / 
p7zip-rar perl-doc pgadmin3 pgadmin3-data subversion subversion-tools gawk zope-common / 
pgagent gsfonts-x11 libgl1-mesa-dri xutils byacc perl-byacc libtiff-doc libtiff-opengl / 
libtiff-tools libtiff4-dev libtiffxx0c2 libpng12-dev swig swig-doc ipython unzip spe / 
libcunit1-doc libcunit1-ncurses-dev python-zodb automake dblatex xsltproc docbook / 
docbook-defguide docbook-html-forms docbook-jrefentry docbook-xsl-doc-html / 
docbook-xsl-doc-pdf docbook-xsl-doc-text docbook-xsl-saxon docbook-xsl-saxon-gcj / 
docbook2x docbook-dsssl libfreetype6-dev libicu4j-java xml2 python-libxml2-dbg / 
libxml2-dbg libxml2-dev libxml2-doc libltdl-dev pkg-config boost-build / 
libboost1.40-all-dev libboost1.40-dbg libboost1.40-dev libboost1.40-doc libgle3 / 
libgle3-dev python-opengl libopengl-perl imagemagick imagemagick-dbg imagemagick-doc / 
postgresql-plperl-8.4 postgresql-pltcl-8.4 postgresql-server-dev-8.4 / 
postgresql-plpython-8.4 subversion lib32ncurses5 lib32ncurses5-dev lib32ncursesw5 / 
lib32ncursesw5-dev libcurses-perl libncurses5-dbg libncurses5-dev libncursesw5-dbg / 
libncursesw5-dev libjpeg62-dbg libjpeg62-dev libopenjpeg2 libopenjpeg2-dbg optipng / 
fftw-dev fftw-docs libfftw3-3 libfftw3-dev libfftw3-doc python-cairo python-cairo-dbg / 
python-cairo-dev libcairo2-dbg libcairo2-dev libcairo2-doc libcairomm-1.0-1 / 
libcairomm-1.0-dev libcairomm-1.0-doc libapache2-mod-wsgi libjava-gnome-jni / 
libswt-gtk-3.5-jni python-cjson python-cjson-dbg
```


### Step 2: Django Installation ###

```
cd /usr/local/src/
sudo svn co http://code.djangoproject.com/svn/django/trunk/ django
cd /usr/local/src/django
sudo python setup.py install
sudo ln -s /usr/local/src/django/ /usr/lib/python2.6/dist-packages/
sudo ln -s /usr/local/src/django/bin/django-admin.py /usr/local/bin
```


### Step 3: GEOS Installation ###

```
cd /usr/local/src/
sudo wget http://download.osgeo.org/geos/geos-3.2.2.tar.bz2
sudo tar -xvf geos-3.2.2.tar.bz2
sudo rm -rf geos-3.2.2.tar.bz2
cd geos-3.2.2/
sudo ./configure --enable-python
sudo make
sudo make install
```


### Step 4: PROJ Installation ###

```
cd /usr/local/src
sudo wget http://download.osgeo.org/proj/proj-4.7.0.tar.gz
sudo tar -xvf proj-4.7.0.tar.gz
sudo rm -rf proj-4.7.0.tar.gz
cd proj-4.7.0/nad/
sudo wget wget ftp://ftp.remotesensing.org/proj/proj-datumgrid-1.5.zip
sudo unzip proj-datumgrid-1.5.zip
sudo rm -rf proj-datumgrid-1.5.zip
cd ../
sudo ./configure
sudo make
sudo make install
cd /etc/ld.so.conf.d/
sudo ln -s /usr/local/lib/libproj.so.0
sudo ldconfig
```


### Step 5: GDAL Installation ###

```
cd /usr/local/src/
sudo wget http://download.osgeo.org/gdal/gdal-1.7.2.tar.gz
sudo tar -xvf gdal-1.7.2.tar.gz
sudo rm -rf gdal-1.7.2.tar.gz
cd gdal-1.7.2/
sudo ./configure --with-python
sudo make
sudo make install
```


### Step 6: GRASS Installation ###

```
cd /usr/local/src/
sudo wget http://grass.osgeo.org/grass64/source/grass-6.4.0RC6.tar.gz
sudo tar -xvf grass-6.4.0RC6.tar.gz
sudo rm -rf grass-6.4.0RC6.tar.gz
cd grass-6.4.0RC6/
sudo ./configure --enable-64bit --with-cxx --with-python=/usr/bin/python2.6-config --without-tcltk --without-opengl --with-freetype-includes='/usr/include/freetype2' --with-postgres --with-postgres-includes='/usr/include/postgresql' --with-x --with-cairo
sudo make
sudo make install
```


### Step 7: PostGIS Installation ###

```
cd /usr/local/src/
sudo wget http://postgis.refractions.net/download/postgis-1.5.1.tar.gz
sudo tar -xvf postgis-1.5.1.tar.gz
sudo rm -rf postgis-1.5.1.tar.gz
cd postgis-1.5.1/
sudo ./configure
sudo make
sudo make install
```


### Step 8: Mapnik Installation ###

```
cd /usr/local/src/
svn co http://svn.mapnik.org/tags/release-0.7.1 mapnik
cd mapnik/
sudo python scons/scons.py configure
sudo python scons/scons.py BOOST_INCLUDES=/usr/include/boost/
sudo python scons/scons.py install
sudo nano /etc/ld.so.conf.d/mapnik.conf
```

Insert the following line into the newly created text file
```
/usr/local/lib64
```
save and exit
```
sudo ldconfig
```