
library(ggplot2)
library(dplyr)
library(scales)

# Load results
ratios <- read.csv("results/citation_fairness_ratios.csv")

# Set category order
ratios$category <- factor(
  ratios$category,
  levels = rev(ratios$category)
)

# Colours matching your website
fairness_colors <- c(
  "Non-profit and academic friendly" = "#4DB6A3",
  "For-profit and academic friendly" = "#2D6381",
  "For-profit and non-academic friendly" = "#AAB8B2"
)

# Create figure
p_fairness <- ggplot(
  ratios,
  aes(x = ratio, y = category, fill = category)
) +
  geom_col(width = 0.55) +
  geom_text(
    aes(label = percent(ratio, accuracy = 1)),
    hjust = -0.2,
    size = 4.5,
    color = "#233D35"
  ) +
  scale_fill_manual(values = fairness_colors) +
  scale_x_continuous(
    limits = c(0, 1.12),
    breaks = NULL,
    expand = expansion(mult = c(0, 0))
  ) +
  labs(x = NULL, y = NULL) +
  theme_minimal(base_size = 12) +
  theme(
    legend.position = "none",
    panel.grid = element_blank(),
    axis.text.y = element_text(
      color = "#1F2421",
      size = 11
    ),
    axis.text.x = element_blank(),
    plot.margin = margin(12, 30, 12, 12),
    plot.background = element_rect(
      fill = "#FAFAF7",
      color = NA
    )
  )

# Display
print(p_fairness)

# Save as SVG
dir.create("images", showWarnings = FALSE)

ggsave(
  "images/citation_fairness.svg",
  p_fairness,
  width = 9,
  height = 2.8,
  bg = "#FAFAF7"
)
