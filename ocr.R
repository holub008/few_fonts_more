library(tesseract)
library(dplyr)

# note: it is possible to do this in python with pytesseract, but the API is horrible
eng <- tesseract("eng", options = list(
  tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ "
))

character_location <- "~/few_fonts_more/images/extracted_characters"
all_files <- list.files(character_location)

certain_characters <- data.frame()

for (character_file in all_files) {
  if (startsWith(character_file, "eroded")) {
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
