% Load the data from the CSV file
data = readtable('drag_data_forced_80.csv');

% Disregard the first 100 rows due to transient
data = data(201:end, :);

% Extract the relevant columns
time = data{:, 1};          % Time column
drag_Re80 = data{:, 2};     % Drag for Re=80
drag_Re150 = data{:, 3};    % Drag for Re=150
drag_Re300 = data{:, 4};    % Drag for Re=300

% Time-averaged drag values
avg_drag_Re80 = 1.37;
avg_drag_Re150 = 1.12;
avg_drag_Re300 = 1.02;

% Define professional colors
navyBlue = [0, 0.1, 0.4];  % Navy Blue
forestGreen = [0.13, 0.55, 0.13]; % Forest Green
darkOrange = [0.85, 0.33, 0.1]; % Dark Orange

% Plot the data
figure;
h1 = plot(time, drag_Re80, '-', 'Color', navyBlue, 'LineWidth', 0.75); % Plot drag for Re=80 with navy blue
hold on;
h2 = plot(time, drag_Re150, '-', 'Color', forestGreen, 'LineWidth', 0.75); % Plot drag for Re=150 with forest green
h3 = plot(time, drag_Re300, '-', 'Color', darkOrange, 'LineWidth', 0.75); % Plot drag for Re=300 with dark orange

% Add dotted lines for average drag
yline(avg_drag_Re80, '--', 'Color', navyBlue, 'LineWidth', 0.75); % Average drag for Re=80 with navy blue
yline(avg_drag_Re150, '--', 'Color', forestGreen, 'LineWidth', 0.75); % Average drag for Re=150 with forest green
yline(avg_drag_Re300, '--', 'Color', darkOrange, 'LineWidth', 0.75); % Average drag for Re=300 with dark orange

% Add labels and title
xlabel('Time(s)');
ylabel('Drag');
%title('Drag vs Time for Different Reynolds Numbers');
legend([h1, h2, h3], 'Re = 80', 'Re = 150', 'Re = 300'); % Legend only for the solid lines

% Optional: Adjust the plot
%grid on;  % Add a grid for better readability

hold off;

