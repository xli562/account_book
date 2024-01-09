def calculate_mean_exchange_rates(data_list):
    rate_sums = {}
    rate_counts = {}

    # Iterate through each dictionary in the list
    for entry in data_list:
        entry:dict
        exchange_rates = entry.get('exchange_rates', {})

        # Process each key-value pair in 'exchange_rates'
        for key, value in exchange_rates.items():
            rate_sums[key] = rate_sums.get(key, 0) + value
            rate_counts[key] = rate_counts.get(key, 0) + 1

    # Calculate the mean for each key
    mean_rates = {key: rate_sums[key] / rate_counts[key] for key in rate_sums}

    return mean_rates

# Example usage
data_list = [
    {'exchange_rates': {'aa': 8.5, 'bb': 8.0}},
    {'exchange_rates': {'aa': 8.7, 'bb': 8.0, 'cc': 9.0}}
]

mean_exchange_rates = calculate_mean_exchange_rates(data_list)
print(mean_exchange_rates)
