import Tree from "file-tree";
import { useEffect, useState } from "react";

export default function FileManager() {
  const [structure, setStructure] = useState(null);
  const [loaded_path, setLoadedPath] = useState(null);
  const tags = ["tag-1"];

  useEffect(() => {
    fetch("/api/files")
      .then((response) => {
        console.log(response);
        console.log(response.json());
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log(data);
        setStructure(data);
      })
      .catch((error) => console.error("Error loading file structure:", error));
  }, []);

  useEffect(() => {
    setStructure({
      test: {
        type: "folder",
        "full-path": "test",
        children: {
          "test.txt": {
            type: "file",
            "full-path": "test/test.txt",
            tags: [],
          },
        },
      },
      test2: {
        type: "folder",
        "full-path": "test2",
        children: {
          "test-2.json": {
            type: "file",
            "full-path": "test-2.json",
            tags: ["tag-1"],
          },
        },
      },
    });
  }, []);

  function createNewFile(path) {
    const new_structure = { ...structure };
    const parts = path.split("/");
    let current = new_structure;

    for (let i = 0; i < parts.length - 1; i++) {
      current = current[parts[i]].children;
    }

    const filename = parts[parts.length - 1];
    current[filename] = {
      type: "file",
      "full-path": path,
      tags: [],
    };

    setStructure(new_structure);
  }

  function createNewFolder(path) {
    const new_structure = { ...structure };
    const parts = path.split("/");
    let current = new_structure;

    for (let i = 0; i < parts.length - 1; i++) {
      current = current[parts[i]].children;
    }

    const folderName = parts[parts.length - 1];
    current[folderName] = {
      type: "folder",
      "full-path": path,
      children: {},
    };

    setStructure(new_structure);
  }

  function deleteObjectPath(path) {
    const new_structure = { ...structure };
    const parts = path.split("/");
    let current = new_structure;

    for (let i = 0; i < parts.length - 1; i++) {
      current = current[parts[i]].children;
    }

    delete current[parts[parts.length - 1]];
    setStructure(new_structure);
  }

  function moveObjectPath(path, new_path) {
    const new_structure = { ...structure };
    const parts = path.split("/");
    let current = new_structure;

    for (let i = 0; i < parts.length - 1; i++) {
      current = current[parts[i]].children;
    }

    // Get a reference to the object being moved
    const objectToMove = current[parts[parts.length - 1]];

    // Remove the object from its current location
    delete current[parts[parts.length - 1]];

    objectToMove["full-path"] = new_path;
    current = new_structure;
    const new_parts = new_path.split("/");
    for (let i = 0; i < new_parts.length - 1; i++) {
      current = current[new_parts[i]].children;
    }

    current[new_parts[new_parts.length - 1]] = objectToMove;

    setStructure(new_structure);
  }

  function copyObjectPath(path, new_path) {
    const new_structure = { ...structure };
    const parts = path.split("/");
    let current = new_structure;

    for (let i = 0; i < parts.length - 1; i++) {
      current = current[parts[i]].children;
    }

    const objectToCopy = { ...current[parts[parts.length - 1]] };
    objectToCopy["full-path"] = new_path;

    const new_parts = new_path.split("/");
    for (let i = 0; i < new_parts.length - 1; i++) {
      current = current[new_parts[i]].children;
    }

    current[new_parts[new_parts.length - 1]] = objectToCopy;
    setStructure(new_structure);
  }

  function loadObjectPath(path) {
    const parts = path.split("/");
    let current = structure;

    for (let i = 0; i < parts.length - 1; i++) {
      current = current[parts[i]].children;
    }

    const objectToLoad = current[parts[parts.length - 1]];

    setLoadedPath(objectToLoad["full-path"]);
  }

  return (
    <div className="w-full mt-5">
      {structure ? (
        <Tree
          treeTitle="Visualization Files"
          structure={structure}
          filterable_tags={tags}
          createNewFile={createNewFile}
          createNewFolder={createNewFolder}
          deletePath={deleteObjectPath}
          move={moveObjectPath}
          copy={copyObjectPath}
          load={loadObjectPath}
        />
      ) : null}
      {loaded_path ? (
        <div className="text-2xl font-bold text-center" data-cy="loaded-path">
          Loaded Path: {loaded_path}
        </div>
      ) : null}
    </div>
  );
}
