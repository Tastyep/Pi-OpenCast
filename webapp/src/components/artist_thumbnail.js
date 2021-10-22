import Box from "@mui/material/Box";
import ImageList from "@mui/material/ImageList";
import ImageListItem from "@mui/material/ImageListItem";

const ArtistThumbnail = ({ albums }) => {
  return (
    <Box
      sx={{
        display: "flex",
        height: "100%",
        width: "100%",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#F0F0F0",
        borderRadius: "5%",
        overflow: "hidden",
      }}
    >
      <ImageList cols={2} gap={0} sx={{ width: "100%", height: "100%" }}>
        {[0, 1, 2, 3].map((index) => (
          <ImageListItem key={index}>
            <img
              src={albums[index % albums.length].thumbnail}
              alt={albums[index % albums.length].name}
              loading="lazy"
            />
          </ImageListItem>
        ))}
      </ImageList>
    </Box>
  );
};

export default ArtistThumbnail;
