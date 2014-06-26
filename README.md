NASindex
========

Indexing service for Network Attached Storage servers and it's contents

## Introduction

This is based on a well known and publicized vulnerability in Iomega NAS servers: no credential access out of the box. And this problem has been ignored for years.
These servers can be easily found using Shodan, just for a person to go through every server by hand might not be impossible just a lot of work.
Therefor to stress once again that this is a major vulnerability I hereby present an indexing service that not only indexes the servers but also it's contents. And eventhough some servers on the homepage state that nothing is being shared, by appending <code>/foldercontent.html</code> to the url this is usually bypassed.

## Operating principle

1. We start by fetching some servers from shodan, either through the API or by importing an .xml file.
2. With curl we fetch the headers of each server to verify that they are live and are in fact an Iomega server.
3. With phantomjs we go to the <code>/foldercontent.html</code> page from which the root folders are fetched which then can be used as a seed for the crawler.

## Current state

This is still a work in progress but where it's at right now is:
* Moved from SQLite to MySQL, so multiple crawlers can be run and simultanious write operations can be performed.
* Import Shodan results through the API (single page for now).
* Fetch headers to confirm if live and an Iomega server.
* Get root folders of the server.

First things to be done:
For the following the theoretical basis is done, only needs to be converted in to actual code:
* Create fingerprinting based on IP address and unique root folders to prevent spending time on crawling the same server over and over.
* Create crawler that goes through each folder and indexes all of it's contents.

As soon as that's all done make it into a search service.

And as a sample output I included an export from the MySQL table that contains IP addresses and root folder, some root folders might not be present as the crawler hasn't gone by.
