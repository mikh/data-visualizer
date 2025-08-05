import Tree from "file-tree";
import { useEffect, useState } from "react";
import {
  copyObject,
  createFolder,
  deleteObject,
  loadObject,
  loadTree,
  moveObject,
  uploadFile,
} from "./FileManagerInterface";

const URL_PREFIX = import.meta.env.VITE_URL_PREFIX || "http://127.0.0.1:5000";

export default function FileManager() {
  const [structure, setStructure] = useState(null);
  const [tags, setTags] = useState([]);
  const [loaded_file, setLoadedFile] = useState(null);

  useEffect(() => {
    loadTree(setStructure, setTags);
  }, []);

  console.log("loaded file", loaded_file);

  return (
    <div className="w-full mt-5">
      {structure ? (
        <Tree
          treeTitle="Visualization Files"
          structure={structure}
          filterable_tags={tags}
          createNewFile={null}
          createNewFolder={(path) => createFolder(path, setStructure, setTags)}
          deletePath={(path) => deleteObject(path, setStructure, setTags)}
          move={(src, dst) => moveObject(src, dst, setStructure, setTags)}
          copy={(src, dst) => copyObject(src, dst, setStructure, setTags)}
          load={(path) => loadObject(path, setLoadedFile)}
          uploadFile={(file, path) =>
            uploadFile(file, path, setStructure, setTags)
          }
        />
      ) : null}
    </div>
  );
}
