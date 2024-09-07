%CP pressure plotter
% Load the data from the CSV file
data = readtable('cp_vs_time_Re_forced_80.csv');

% Extract the relevant columns
time = data{:, 1};          % Time column
Cp_Re80 = data{:, 2};       % Cp for Re=80
Cp_Re150 = data{:, 3};      % Cp for Re=150
Cp_Re300 = data{:, 4};      % Cp for Re=300

% Define professional colors
navyBlue = [0, 0.1, 0.4];  % Navy Blue
forestGreen = [0.13, 0.55, 0.13]; % Forest Green
darkOrange = [0.85, 0.33, 0.1]; % Dark Orange
% Plot the data
figure;
h1 = plot(time, Cp_Re80, 'Color', navyBlue, 'LineWidth', 0.75); % Plot Cp for Re=80
hold on;
h2 = plot(time, Cp_Re150, 'Color',forestGreen, 'LineWidth', 0.75); % Plot Cp for Re=150
h3 = plot(time, Cp_Re300, 'Color',darkOrange, 'LineWidth', 0.75); % Plot Cp for Re=300

% Add labels and title
xlabel('Time (s)');
ylabel('Pressure Coefficient (Cp)');
%title('Cp vs Time for Different Reynolds Numbers');
legend([h1, h2, h3], 'Re = 80', 'Re = 150', 'Re = 300', 'Location', 'northwest'); % Move legend to the top-right corner

% Optional: Adjust the plot
% grid on;  % Add a grid for better readability

hold off;




