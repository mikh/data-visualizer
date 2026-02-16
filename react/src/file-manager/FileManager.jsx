import Tree from "file-tree";
import { useEffect, useState } from "react";
import {
  copyObject,
  deleteObject,
  loadObject,
  loadTree,
  moveObject,
  uploadFile,
} from "./FileManagerInterface";
import DataViewer from "../data-viewer/DataViewer";

export default function FileManager({ setLoadedFile }) {
  const [structure, setStructure] = useState(null);
  const [tags, setTags] = useState([]);

  useEffect(() => {
    loadTree(setStructure, setTags);
  }, []);

  return (
    <div className="flex w-full mt-5 gap-4 px-4">
      <div className="w-72 flex-shrink-0">
        {structure ? (
          <Tree
            treeTitle="Visualization Files"
            structure={structure}
            filterable_tags={tags}
            createNewFile={null}
            createNewFolder={null}
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
      <div className="flex-1 min-w-0">
        <DataViewer loadedFile={loaded_file} />
      </div>
    </div>
  );
}
