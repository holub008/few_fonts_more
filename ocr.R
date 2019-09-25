library(tesseract)
library(dplyr)
library(imager)

# note: it is possible to do this in python with pytesseract, but the API is horrible
eng <- tesseract("eng", options = list(
  tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ "
))

character_location <- "/Users/kholub/few_fonts_more/images/extracted_characters"
all_files <- list.files(character_location)

certain_characters <- data.frame()

for (character_file in all_files) {
  if (startsWith(character_file, "tesseract")) {
    content <- ocr_data(paste0(character_location, '/', character_file), eng)
    if (nrow(content) > 0) {
            matches <- content %>% 
              filter(confidence == max(confidence)) %>%
              mutate(file=character_file)
            if (nrow(matches) == 1) {
              certain_characters <- rbind(certain_characters, matches,
                                          stringsAsFactors=FALSE)
            }
              
    }
  }
}

certain_characters %>% 
  filter(nchar(word) == 1) %>%
  group_by(word) %>%
  count() %>%
  View()

certain_characters %>%
  ggplot() + geom_histogram(aes(confidence))

mean(certain_characters$confidence)

certain_characters %>%
  filter(word == 'J')

plot_averaged_character <- function(characters, letter) {
  characters %>%
    filter(word == letter) %>%
    pull(file) %>%
    sapply(function(file) {
      return(load.image(paste0(character_location, '/', file)))
    }) %>%
    lapply(function(img) {
      return(resize(img, 200, 200))
    }) %>%
    average() %>%
    plot()
}

for (letter in c('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'K', 'R', 'S', 'X', 'Z')) {
  plot_averaged_character(certain_characters, letter)
}
