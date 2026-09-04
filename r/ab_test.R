library(readr)
library(dplyr)
library(ggplot2)

data <- read_csv("data/processed/clean_ab_data.csv")

# General data exploration

sum(is.na(data))
mean(data, na.rm = TRUE)
glimpse(data)
dim(data)
names(data)

# 5.1 Summarize the experiment and effect size

library(scales)

control_rate <- summary_stats |> 
  filter(group == "control") |> 
  pull(conversion_rate)

treatment_rate <- summary_stats |> 
  filter(group == "treatment") |> 
  pull(conversion_rate)

summary_stats <- summary_stats |> 
  mutate(
    absolute_lift = (treatment_rate - control_rate)*100,
    relative_lift = percent(absolute_lift / control_rate, accuracy = 0.01)
  )

# 5.2 Test the conversion-rate difference

# H0: the treatment and control population conversion rates are equal.
# H1: the treatment and control population conversion rates are different.


# 5.2.3

total_control <- summary_stats |> 
  filter(group == "control") |> 
  pull(users)

total_treatment <- summary_stats |> 
  filter(group == "treatment") |> 
  pull(users)
  
x <- c(treatment_rate, control_rate)  # successes
n <- c(total_treatment, total_control)  # trials

proportion_test <- prop.test(x, n, correct = FALSE)

#5.2.4
p_value <- proportion_test$p.value
confidence_interval <- proportion_test$conf.int

# 5.2.5
if (p_value < 0.05) {
  cat("Decision: REJECT H0\n")
} else {
  cat("Decision: FAIL TO REJECT H0\n")
}

# 5.3 Create and explain two ggplot2 figures

# 5.3.1
bar_plot <- ggplot(summary_stats, aes(x = group, y = conversion_rate, fill = group)) +
  geom_col(width = 0.5, show.legend = FALSE) +
  geom_text(
    aes(label = percent(conversion_rate, accuracy = 0.1)),
    vjust = -0.5, 
    fontface = "bold",
    size = 4
  ) +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, max(summary_stats$conversion_rate) * 1.25)) +
  scale_fill_manual(values = c("control" = "#14919B", "treatment" = "#11558C")) +
  labs(
    title = "Conversion Rate Comparison by Group",
    x = "Group",
    y = "Conversion Rate (%)"
  ) +
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0.5),
    panel.grid.major.x = element_blank()
  )

# 5.3.2

data <- data |> 
mutate(experiment_date = as.Date(timestamp))

daily_stats <- data |> 
  group_by(experiment_date, group) |> 
  summarise(
    daily_conversion_rate = mean(converted),
    .groups = "drop"
  )

line_plot <- ggplot(daily_stats, aes(x = as.Date(experiment_date), y = daily_conversion_rate, color = group, group = group)) +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  scale_y_continuous(labels = percent_format(accuracy = 1)) +
  scale_x_date(date_breaks = "3 days", date_labels = "%b %d") +
  scale_color_manual(values = c("control" = "#E1A16C", "treatment" = "#4378A6"), name = "Group") +
  labs(
    title = "Daily Conversion Rate Trend",
    x = "Experiment Date",
    y = "Conversion Rate (%)"
  ) +
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0.5),
    legend.position = "top"
  )

# 5.3.3
ggsave("outputs/figures/bar_conversion_rate_comparison.png", plot = bar_plot, width = 6, height = 5, dpi = 300)
ggsave("outputs/figures/line_daily_conversion_trend.png", plot = line_plot, width = 8, height = 5, dpi = 300)