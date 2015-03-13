## Configuring Postgres with PostGIS ##


### Step 1:  Set the password for the postgres system user ###

```
sudo passwd postgres
```


### Step 2:  Create your own unique user for postgres & postGIS ###

```
sudo adduser NEWUSERNAME
```


### Step 3:  Add the user to the proper groups ###

```
sudo nano /etc/group
```

Add NEWUSERNAME to the adm & admin groups

Then add the NEWUSERNAME to the sudoers file

```
sudo nano /etc/sudoers
```

Add the following line below the last user:
```
NEWUSERNAME ALL=(ALL) NOPASSWD:ALL
```


### Step 4:  Enter the postgres system user & edit the pg\_hba.fonf file ###

```
su postgres

nano /etc/postgresql/8.3/main/pg_hba.conf 
```

Comment out the following line:
```
(local   all    all       ident sameuser)
```

And add the following lines at the end to allow password authentication & local connections:

```
host    all     all     0.0.0.0/0       md5
local   all     all             trust
```


### Step 5:  Edit the postgresql.conf file ###

```
nano /etc/postgresql/8.3/main/postgresql.conf
```

Add the following items to the connection settings line "listen address" and uncomment the line:
```
localhost, PUBLIC DNS NAME, PRIVATE DNS NAME & ELASTIC IP
```

Example:
```
listen_addresses = 'localhost,144.139.268.168,ec2-144-139-268-168.compute-1.amazonaws.com,10-223-182-168'
```


### Step 6:  Set the password for the postgres database user ###

Enter postgresql
```
psql
```
Set the password
```
\password postgres
```

### Step 7: Create the NEWUSERNAME database user ###

While in the psql command line interface logged in as postgres:
```
CREATE USER gisdev SUPERUSER;
```
Set the password for the gisdev user
```
\password gisdev
```


### Step 8:  Exit postgres, the postgres user, and restart postgresql ###

```
\q
exit
sudo /etc/init.d/postgresql-8.3 restart
```