function [fig] = PlotWrapper(func_name, save_path, varargin)

%% PURPOSE: WRAPPER FUNCTION TO PLOT DATA

v = varargin{1};

try
    fig = feval(func_name, v{:});
catch
    v(end) = [];
    fig = feval(func_name, v{:});
end

% Save the figure
saveas(fig, save_path, 'fig');
saveas(fig, save_path, 'png');
saveas(fig, save_path, 'svg');

close(fig);

end