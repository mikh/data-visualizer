import { useState } from "react";

import Header from "./Header.jsx";
import FileManager from "./file-manager/FileManager.jsx";
import FileDisplay from "./file-display/FileDisplay.jsx";
import DataViewer from "./data-viewer/DataViewer.jsx";

export default function App() {
  const [loadedFile, setLoadedFile] = useState(null);

  return (
    <div>
      <Header />
      <FileManager setLoadedFile={setLoadedFile} />
      {loadedFile ? <FileDisplay loadedFile={loadedFile} /> : null}
      <DataViewer loadedFile={loadedFile} />
    </div>
  );
}
