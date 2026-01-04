import FileStats from "./FileStats";
import TagDisplay from "./TagDisplay";

export default function FileDisplay({ loadedFile }) {
  console.log("loaded file", loadedFile);

  return (
    <div
      style={{ fontFamily: "Philosopher" }}
      className="flex flex-col items-center justify-center"
    >
      <h1 className="text-2xl">{loadedFile.name}</h1>
      <p className="text-sm italic">{loadedFile.path}</p>
      <p className="text-sm italic">{loadedFile.data_file_type} file</p>
      <TagDisplay tags={loadedFile.tags} />
      {loadedFile.file_stats ? (
        <FileStats fileStats={loadedFile.file_stats} />
      ) : null}
    </div>
  );
}
