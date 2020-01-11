library(tesseract)
library(dplyr)
library(imager)
library(ggplot2)

# note: it is possible to do this in python with pytesseract, but the API is horrible
eng <- tesseract("eng", options = list(
  tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ "
))

character_location <- "/Users/kholub/few_fonts_more/images/extracted_characters"
all_files <- list.files(character_location)

certain_characters <- data.frame()

for (character_file in all_files) {
  if (startsWith(character_file, "tesseract")) {
    tail <- gsub('tesseract', '', character_file)
    content <- ocr_data(paste0(character_location, '/', character_file), eng)
    if (nrow(content) > 0) {
            matches <- content %>% 
              filter(confidence == max(confidence)) %>%
              mutate(file=paste0('mask', tail))
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

plot_averaged_character <- function(characters, letter, conf_level=.5) {
  characters %>%
    filter(word == letter) %>%
    filter(confidence > conf_level) %>%
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

for (letter in c('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'K', 'R', 'S', 'X', 'Z', 'Y')) {
  plot_averaged_character(certain_characters, letter)
}

# playing with the lin alg for projection onto two intersecting planes
compute_projection <- function(a, e = matrix(c(4,4,1), nrow=3), c_vec=matrix(c(0,0,0), nrow=3)) {
  d <- a - c_vec
  b <- matrix(c(
    e[3] / d[3] * d[1] + e[1],
    e[3] / d[3] * d[2] + e[2]
  ), nrow=2) 
}

shape <- data.frame(
  x=c(1, 2, 3, 4, 5),
  y=c(1, 3, 5, 3, 1),
  z=rep(1, 5)
)

projected_data <- data.frame()
for (ix in 1:nrow(shape)) {
  a <- t(as.matrix(unname(shape[ix,])))
  a_prime <- compute_projection(a)
  
  projected_data <- rbind(projected_data, as.vector(a_prime))
}

colnames(projected_data) <- c('x', 'y')

ggplot(projected_data) + geom_point(aes(x, y))
