# Objectives

Main objectives of data visualizer is to create a single view that is able to show both data and
results from data analysis in a single seamless view.

The main pieces needed here are:

1. File structure and manipulation
1. Display of non-graph-based data
1. Generic Graph Interface
1. Graph Implementations
1. Raw SQL Queries?

## File Structure and Manipulation

Files need to be uploaded and manipulated within the graph view. This should allow the following
functionality:

1. Create Folder
1. Delete Folder
1. Move Folder
1. Copy Folder
1. Upload File
1. Move File
1. Delete File
1. Copy File
1. Load File

We need to add a layer of indirection here, since some data formats for incoming files will have the ability to store metadata, and others won't. So we will not want to make the display be one-to-one, but instead, display a metadata file, that has the actual file underneath it. When a given file is moved around, we move both the metadata file, as well as the actual file.

Perhaps an easier way to solve this is by using a database which stores information and metadata. Files that are uploaded will be stored in a flat directory, and their metadata will be pushed to the database which will maintain the appearance of a folder structure in the front end.

## Display of non-graph-based data

In each files, some of the fields are not in a tabular format, and usually represent metadata about
the contained information, or general statistics. This should display that data in an easy to read
way.

## Generic Graph Interface

Before we can display different graphs, we need an interface that allows selection of the
parameters, and the graph fields to use. This includes:

1. Selection of Graph Type
1. Selection of Columns based on graph type selection

## Graph Implementations

Once we have a selection interface, we need to display the different graphs. The ones slated for
initial support are:

1. Line
1. Scatter
1. Bar
1. Heat Map

## Raw SQL Queries?

In the initial implementation of this, we generated the SQL files for ad-hoc analysis of a dataset.
Perhaps we can add support for this later.
