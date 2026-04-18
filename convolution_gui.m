function convolution_gui()
% ==========================================================
% Program Convolution / Mask Processing (Peningkatan Mutu Citra)
% Pengolahan Citra Digital - MATLAB GUI
% ==========================================================
% Mendukung citra BERWARNA (RGB) - konvolusi per channel R, G, B
% ==========================================================

    % ---- Figure Utama ----
    fig = figure('Name', 'Convolution (RGB) - PCD', ...
                 'NumberTitle', 'off', ...
                 'Position', [60 60 1350 780], ...
                 'MenuBar', 'none', ...
                 'ToolBar', 'none', ...
                 'Color', [0.12 0.12 0.18], ...
                 'Resize', 'on');
    
    % ---- Data ----
    data.img_original = [];  % RGB
    data.img_result = [];    % RGB
    data.kernel_name = '';
    guidata(fig, data);
    
    % ---- Kernel definitions ----
    kernel_names = {'Mean Filter 3x3', 'Mean Filter 5x5', ...
                    'Gaussian 3x3', 'Gaussian 5x5', ...
                    'Sharpen (Laplacian)', 'Sharpen (High-Boost)', ...
                    'Edge - Laplacian', ...
                    'Edge - Sobel Horizontal', 'Edge - Sobel Vertical', ...
                    'Edge - Prewitt Horizontal', 'Edge - Prewitt Vertical', ...
                    'Emboss'};
    
    kernels = cell(1, length(kernel_names));
    kernels{1}  = ones(3,3)/9;
    kernels{2}  = ones(5,5)/25;
    kernels{3}  = [1 2 1; 2 4 2; 1 2 1]/16;
    kernels{4}  = [1 4 6 4 1; 4 16 24 16 4; 6 24 36 24 6; 4 16 24 16 4; 1 4 6 4 1]/256;
    kernels{5}  = [0 -1 0; -1 5 -1; 0 -1 0];
    kernels{6}  = [-1 -1 -1; -1 9 -1; -1 -1 -1];
    kernels{7}  = [0 -1 0; -1 4 -1; 0 -1 0];
    kernels{8}  = [-1 -2 -1; 0 0 0; 1 2 1];
    kernels{9}  = [-1 0 1; -2 0 2; -1 0 1];
    kernels{10} = [-1 -1 -1; 0 0 0; 1 1 1];
    kernels{11} = [-1 0 1; -1 0 1; -1 0 1];
    kernels{12} = [-2 -1 0; -1 1 1; 0 1 2];
    
    % ---- UI Colors ----
    btn_color = [0.54 0.71 0.98];
    btn_fg = [0.12 0.12 0.18];
    lbl_fg = [0.80 0.84 0.96];
    sidebar_bg = [0.09 0.09 0.15];
    
    % ---- Title ----
    uicontrol('Style', 'text', 'String', 'Convolution / Mask Processing (RGB) - PCD', ...
              'Position', [20 740 550 30], 'FontSize', 14, 'FontWeight', 'bold', ...
              'ForegroundColor', lbl_fg, 'BackgroundColor', [0.12 0.12 0.18], ...
              'HorizontalAlignment', 'left');
    
    % ---- Sidebar Panel ----
    sidebar_panel = uipanel('Parent', fig, 'Position', [0.01 0.04 0.20 0.88], ...
                            'BackgroundColor', sidebar_bg, 'BorderType', 'none');
    
    y_pos = 0.94;
    dy = 0.055;
    
    uicontrol('Parent', sidebar_panel, 'Style', 'pushbutton', ...
              'String', 'Load Citra', ...
              'Units', 'normalized', 'Position', [0.05 y_pos-dy 0.90 dy], ...
              'FontSize', 10, 'FontWeight', 'bold', ...
              'ForegroundColor', btn_fg, 'BackgroundColor', btn_color, ...
              'Callback', @btn_load);
    y_pos = y_pos - 2*dy;
    
    uicontrol('Parent', sidebar_panel, 'Style', 'text', ...
              'String', 'Pilih Kernel / Mask:', ...
              'Units', 'normalized', 'Position', [0.05 y_pos 0.90 0.04], ...
              'FontSize', 9, 'ForegroundColor', lbl_fg, ...
              'BackgroundColor', sidebar_bg, 'HorizontalAlignment', 'left');
    y_pos = y_pos - dy;
    
    kernel_popup = uicontrol('Parent', sidebar_panel, 'Style', 'popupmenu', ...
              'String', kernel_names, ...
              'Units', 'normalized', 'Position', [0.05 y_pos 0.90 0.04], ...
              'FontSize', 9, 'Callback', @popup_kernel_changed);
    y_pos = y_pos - 1.5*dy;
    
    uicontrol('Parent', sidebar_panel, 'Style', 'text', ...
              'String', 'Kernel Matrix:', ...
              'Units', 'normalized', 'Position', [0.05 y_pos 0.90 0.035], ...
              'FontSize', 9, 'ForegroundColor', lbl_fg, ...
              'BackgroundColor', sidebar_bg, 'HorizontalAlignment', 'left');
    y_pos = y_pos - 3*dy;
    
    kernel_text = uicontrol('Parent', sidebar_panel, 'Style', 'text', ...
              'String', '', ...
              'Units', 'normalized', 'Position', [0.05 y_pos 0.90 3*dy], ...
              'FontSize', 8, 'FontName', 'Consolas', ...
              'ForegroundColor', [0.98 0.70 0.53], ...
              'BackgroundColor', [0.19 0.19 0.27], ...
              'HorizontalAlignment', 'left');
    y_pos = y_pos - 1.5*dy;
    
    uicontrol('Parent', sidebar_panel, 'Style', 'text', ...
              'String', 'Custom Kernel 3x3:', ...
              'Units', 'normalized', 'Position', [0.05 y_pos 0.90 0.035], ...
              'FontSize', 9, 'ForegroundColor', lbl_fg, ...
              'BackgroundColor', sidebar_bg, 'HorizontalAlignment', 'left');
    y_pos = y_pos - dy;
    
    custom_edits = gobjects(3,3);
    ew = 0.28; eh = 0.04;
    for row = 1:3
        for col = 1:3
            ex = 0.05 + (col-1)*(ew+0.02);
            ey = y_pos - (row-1)*(eh+0.01);
            custom_edits(row,col) = uicontrol('Parent', sidebar_panel, ...
                'Style', 'edit', 'String', '0', ...
                'Units', 'normalized', 'Position', [ex ey ew eh], ...
                'FontSize', 9, 'FontName', 'Consolas', ...
                'BackgroundColor', [0.19 0.19 0.27], ...
                'ForegroundColor', [0.80 0.84 0.96], ...
                'HorizontalAlignment', 'center');
        end
    end
    y_pos = y_pos - 3*(eh+0.01) - dy;
    
    uicontrol('Parent', sidebar_panel, 'Style', 'pushbutton', ...
              'String', 'Gunakan Custom Kernel', ...
              'Units', 'normalized', 'Position', [0.05 y_pos 0.90 dy], ...
              'FontSize', 9, 'FontWeight', 'bold', ...
              'ForegroundColor', btn_fg, 'BackgroundColor', [0.98 0.70 0.53], ...
              'Callback', @btn_use_custom);
    y_pos = y_pos - 2*dy;
    
    uicontrol('Parent', sidebar_panel, 'Style', 'pushbutton', ...
              'String', 'Terapkan Konvolusi', ...
              'Units', 'normalized', 'Position', [0.05 y_pos 0.90 dy*1.2], ...
              'FontSize', 11, 'FontWeight', 'bold', ...
              'ForegroundColor', btn_fg, 'BackgroundColor', [0.65 0.89 0.63], ...
              'Callback', @btn_apply);
    y_pos = y_pos - 1.5*dy;
    
    uicontrol('Parent', sidebar_panel, 'Style', 'pushbutton', ...
              'String', 'Simpan Hasil', ...
              'Units', 'normalized', 'Position', [0.05 y_pos 0.90 dy], ...
              'FontSize', 10, 'FontWeight', 'bold', ...
              'ForegroundColor', btn_fg, 'BackgroundColor', btn_color, ...
              'Callback', @btn_save);
    y_pos = y_pos - 1.5*dy;
    
    uicontrol('Parent', sidebar_panel, 'Style', 'pushbutton', ...
              'String', 'Reset', ...
              'Units', 'normalized', 'Position', [0.05 y_pos 0.90 dy], ...
              'FontSize', 10, 'FontWeight', 'bold', ...
              'ForegroundColor', btn_fg, 'BackgroundColor', [0.95 0.55 0.66], ...
              'Callback', @btn_reset);
    
    % Status
    status_label = uicontrol('Style', 'text', ...
              'String', 'Siap. Pilih gambar untuk memulai.', ...
              'Position', [20 8 800 20], 'FontSize', 9, ...
              'ForegroundColor', [0.65 0.68 0.78], ...
              'BackgroundColor', sidebar_bg, 'HorizontalAlignment', 'left');
    
    update_kernel_display(kernels{1});
    
    % ===== HELPERS =====
    
    function img = ensure_rgb(img)
        if size(img, 3) == 1
            img = cat(3, img, img, img);
        end
    end
    
    function plot_rgb_hist(ax, img, ttl)
        hold(ax, 'on');
        [cR, ~] = imhist(img(:,:,1));
        [cG, ~] = imhist(img(:,:,2));
        [cB, bins] = imhist(img(:,:,3));
        bar(ax, bins, cR, 'FaceColor', [1 0.4 0.4], 'FaceAlpha', 0.5, 'EdgeColor', 'none');
        bar(ax, bins, cG, 'FaceColor', [0.3 0.8 0.4], 'FaceAlpha', 0.5, 'EdgeColor', 'none');
        bar(ax, bins, cB, 'FaceColor', [0.2 0.6 0.9], 'FaceAlpha', 0.5, 'EdgeColor', 'none');
        hold(ax, 'off');
        title(ax, ttl, 'Color', lbl_fg, 'FontSize', 10);
        legend(ax, 'R', 'G', 'B', 'TextColor', lbl_fg, 'Color', [0.19 0.19 0.27], ...
               'EdgeColor', [0.27 0.28 0.35], 'FontSize', 7);
        ax.Color = [0.19 0.19 0.27];
        ax.XColor = [0.65 0.68 0.78]; ax.YColor = [0.65 0.68 0.78];
        xlim(ax, [0 255]);
    end
    
    % ===== CALLBACKS =====
    
    function btn_load(~, ~)
        [file, path] = uigetfile({'*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff', ...
                                   'Image Files'}, 'Pilih Citra');
        if isequal(file, 0), return; end
        
        d = guidata(fig);
        img = imread(fullfile(path, file));
        d.img_original = ensure_rgb(img);
        d.img_result = [];
        guidata(fig, d);
        
        set(status_label, 'String', ['Citra dimuat (RGB): ' file]);
        show_original(d);
    end
    
    function popup_kernel_changed(~, ~)
        idx = get(kernel_popup, 'Value');
        update_kernel_display(kernels{idx});
    end
    
    function btn_use_custom(~, ~)
        try
            k = zeros(3,3);
            for r = 1:3
                for c = 1:3
                    k(r,c) = str2double(get(custom_edits(r,c), 'String'));
                end
            end
            if any(isnan(k(:)))
                errordlg('Semua nilai kernel harus berupa angka!', 'Error');
                return;
            end
            kernel_names{end+1} = 'Custom 3x3';
            kernels{end+1} = k;
            set(kernel_popup, 'String', kernel_names, 'Value', length(kernel_names));
            update_kernel_display(k);
            set(status_label, 'String', 'Custom kernel telah diset.');
        catch
            errordlg('Error membaca custom kernel!', 'Error');
        end
    end
    
    function btn_apply(~, ~)
        d = guidata(fig);
        if isempty(d.img_original)
            msgbox('Silakan load citra terlebih dahulu!', 'Peringatan', 'warn');
            return;
        end
        
        idx = get(kernel_popup, 'Value');
        k = kernels{idx};
        kname = kernel_names{idx};
        
        set(status_label, 'String', ['Memproses konvolusi RGB: ' kname '...']);
        drawnow;
        
        % Konvolusi per channel R, G, B
        result = uint8(zeros(size(d.img_original)));
        for ch = 1:3
            temp = imfilter(double(d.img_original(:,:,ch)), k, 'replicate');
            result(:,:,ch) = uint8(max(0, min(255, temp)));
        end
        
        d.img_result = result;
        d.kernel_name = kname;
        guidata(fig, d);
        
        set(status_label, 'String', ['Konvolusi selesai (RGB): ' kname]);
        show_result(d);
    end
    
    function btn_save(~, ~)
        d = guidata(fig);
        if isempty(d.img_result)
            msgbox('Belum ada hasil untuk disimpan!', 'Peringatan', 'warn');
            return;
        end
        [file, path] = uiputfile({'*.png','PNG';'*.jpg','JPEG';'*.bmp','BMP'}, 'Simpan Hasil');
        if ~isequal(file, 0)
            imwrite(d.img_result, fullfile(path, file));
            set(status_label, 'String', ['Hasil disimpan: ' fullfile(path, file)]);
        end
    end
    
    function btn_reset(~, ~)
        d.img_original = [];
        d.img_result = [];
        d.kernel_name = '';
        guidata(fig, d);
        allAxes = findall(fig, 'Type', 'axes');
        delete(allAxes);
        set(status_label, 'String', 'Siap. Pilih gambar untuk memulai.');
    end
    
    % ===== DISPLAY =====
    
    function update_kernel_display(k)
        str = '';
        for r = 1:size(k,1)
            row_str = '[ ';
            for c = 1:size(k,2)
                row_str = [row_str, sprintf('%7.3f ', k(r,c))]; %#ok
            end
            row_str = [row_str, ']']; %#ok
            str = [str, row_str, newline]; %#ok
        end
        set(kernel_text, 'String', str);
    end
    
    function show_original(d)
        allAxes = findall(fig, 'Type', 'axes');
        delete(allAxes);
        
        ax1 = axes('Parent', fig, 'Position', [0.25 0.12 0.70 0.78]);
        imshow(d.img_original, 'Parent', ax1);
        title(ax1, 'Citra Asli (RGB)', 'Color', lbl_fg, 'FontSize', 13, 'FontWeight', 'bold');
    end
    
    function show_result(d)
        allAxes = findall(fig, 'Type', 'axes');
        delete(allAxes);
        
        ax1 = axes('Parent', fig, 'Position', [0.23 0.53 0.35 0.40]);
        imshow(d.img_original, 'Parent', ax1);
        title(ax1, 'Citra Asli', 'Color', lbl_fg, 'FontSize', 11, 'FontWeight', 'bold');
        
        ax2 = axes('Parent', fig, 'Position', [0.62 0.53 0.35 0.40]);
        imshow(d.img_result, 'Parent', ax2);
        title(ax2, ['Hasil: ' d.kernel_name], 'Color', lbl_fg, 'FontSize', 11, 'FontWeight', 'bold');
        
        ax3 = axes('Parent', fig, 'Position', [0.23 0.06 0.35 0.38]);
        plot_rgb_hist(ax3, d.img_original, 'Histogram Asli (RGB)');
        
        ax4 = axes('Parent', fig, 'Position', [0.62 0.06 0.35 0.38]);
        plot_rgb_hist(ax4, d.img_result, 'Histogram Hasil (RGB)');
    end

end
