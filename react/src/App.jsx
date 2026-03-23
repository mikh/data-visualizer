import { useState } from "react";

import Header from "./Header.jsx";
import Attributions from "./Attributions.jsx";
import FileManager from "./file-manager/FileManager.jsx";
import FileDisplay from "./file-display/FileDisplay.jsx";
import DataViewer from "./data-viewer/DataViewer.jsx";

export default function App() {
  const [loadedFile, setLoadedFile] = useState(null);
  const [showAttributions, setShowAttributions] = useState(false);

  return (
    <div>
      <Header showAttributions={showAttributions} setShowAttributions={setShowAttributions} />
      <Attributions visible={showAttributions} />
      <FileManager setLoadedFile={setLoadedFile} />
      {loadedFile ? <FileDisplay loadedFile={loadedFile} /> : null}
      <DataViewer loadedFile={loadedFile} />
    </div>
  );
}
