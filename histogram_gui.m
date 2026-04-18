function histogram_gui()
% ==========================================================
% Program Histogram Specification (Peningkatan Mutu Citra)
% Pengolahan Citra Digital - MATLAB GUI
% ==========================================================
% Mendukung citra BERWARNA (RGB) - proses per channel R, G, B
% ==========================================================

    % ---- Buat Figure Utama ----
    fig = figure('Name', 'Histogram Specification (RGB) - PCD', ...
                 'NumberTitle', 'off', ...
                 'Position', [80 80 1300 750], ...
                 'MenuBar', 'none', ...
                 'ToolBar', 'none', ...
                 'Color', [0.12 0.12 0.18], ...
                 'Resize', 'on');
    
    % ---- Data Storage ----
    data.img_original = [];   % RGB
    data.img_reference = [];  % RGB
    data.img_equalized = [];
    data.img_specified = [];
    guidata(fig, data);
    
    % ---- UI Colors ----
    btn_color = [0.54 0.71 0.98];
    btn_fg = [0.12 0.12 0.18];
    lbl_fg = [0.80 0.84 0.96];
    lbl_bg = [0.12 0.12 0.18];
    
    % ---- Title ----
    uicontrol('Parent', fig, 'Style', 'text', ...
              'String', 'Histogram Specification (RGB) - Pengolahan Citra Digital', ...
              'Position', [20 700 550 35], ...
              'FontSize', 14, 'FontWeight', 'bold', ...
              'ForegroundColor', lbl_fg, 'BackgroundColor', lbl_bg, ...
              'HorizontalAlignment', 'left');
    
    % ---- Buttons ----
    uicontrol('Style', 'pushbutton', 'String', 'Load Citra Asli', ...
              'Position', [20 660 160 35], 'FontSize', 10, 'FontWeight', 'bold', ...
              'ForegroundColor', btn_fg, 'BackgroundColor', btn_color, ...
              'Callback', @btn_load_original);
    
    uicontrol('Style', 'pushbutton', 'String', 'Load Citra Referensi', ...
              'Position', [190 660 180 35], 'FontSize', 10, 'FontWeight', 'bold', ...
              'ForegroundColor', btn_fg, 'BackgroundColor', btn_color, ...
              'Callback', @btn_load_reference);
    
    uicontrol('Style', 'pushbutton', 'String', 'Histogram Equalization', ...
              'Position', [380 660 190 35], 'FontSize', 10, 'FontWeight', 'bold', ...
              'ForegroundColor', btn_fg, 'BackgroundColor', [0.65 0.89 0.63], ...
              'Callback', @btn_equalization);
    
    uicontrol('Style', 'pushbutton', 'String', 'Histogram Specification', ...
              'Position', [580 660 190 35], 'FontSize', 10, 'FontWeight', 'bold', ...
              'ForegroundColor', btn_fg, 'BackgroundColor', [0.95 0.55 0.66], ...
              'Callback', @btn_specification);
    
    uicontrol('Style', 'pushbutton', 'String', 'Simpan Hasil', ...
              'Position', [780 660 130 35], 'FontSize', 10, 'FontWeight', 'bold', ...
              'ForegroundColor', btn_fg, 'BackgroundColor', btn_color, ...
              'Callback', @btn_save);
    
    uicontrol('Style', 'pushbutton', 'String', 'Reset', ...
              'Position', [1180 660 100 35], 'FontSize', 10, 'FontWeight', 'bold', ...
              'ForegroundColor', btn_fg, 'BackgroundColor', [0.98 0.70 0.53], ...
              'Callback', @btn_reset);
    
    % Status
    status_label = uicontrol('Style', 'text', ...
              'String', 'Siap. Silakan load citra asli untuk memulai.', ...
              'Position', [20 10 800 22], 'FontSize', 9, ...
              'ForegroundColor', [0.65 0.68 0.78], ...
              'BackgroundColor', [0.09 0.09 0.15], ...
              'HorizontalAlignment', 'left');
    
    % ===== HELPER: Ensure RGB =====
    function img = ensure_rgb(img)
        if size(img, 3) == 1
            img = cat(3, img, img, img);
        end
    end
    
    % ===== HELPER: Plot RGB Histogram =====
    function plot_rgb_hist(ax, img, ttl)
        hold(ax, 'on');
        [countsR, ~] = imhist(img(:,:,1));
        [countsG, ~] = imhist(img(:,:,2));
        [countsB, binsB] = imhist(img(:,:,3));
        bar(ax, binsB, countsR, 'FaceColor', [1 0.4 0.4], 'FaceAlpha', 0.5, 'EdgeColor', 'none');
        bar(ax, binsB, countsG, 'FaceColor', [0.3 0.8 0.4], 'FaceAlpha', 0.5, 'EdgeColor', 'none');
        bar(ax, binsB, countsB, 'FaceColor', [0.2 0.6 0.9], 'FaceAlpha', 0.5, 'EdgeColor', 'none');
        hold(ax, 'off');
        title(ax, ttl, 'Color', lbl_fg, 'FontSize', 10);
        legend(ax, 'R', 'G', 'B', 'TextColor', lbl_fg, 'Color', [0.19 0.19 0.27], ...
               'EdgeColor', [0.27 0.28 0.35], 'FontSize', 7);
        ax.Color = [0.19 0.19 0.27];
        ax.XColor = [0.65 0.68 0.78];
        ax.YColor = [0.65 0.68 0.78];
        xlim(ax, [0 255]);
    end
    
    % ===== HELPER: Equalize one channel =====
    function out = eq_channel(ch)
        out = histeq(ch);
    end
    
    % ===== HELPER: Specify one channel =====
    function out = spec_channel(src_ch, ref_ch)
        out = imhistmatch(src_ch, ref_ch);
    end
    
    % ===== CALLBACKS =====
    
    function btn_load_original(~, ~)
        [file, path] = uigetfile({'*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff', ...
                                   'Image Files'}, 'Pilih Citra Asli');
        if isequal(file, 0), return; end
        
        d = guidata(fig);
        img = imread(fullfile(path, file));
        d.img_original = ensure_rgb(img);
        d.img_equalized = [];
        d.img_specified = [];
        guidata(fig, d);
        
        set(status_label, 'String', ['Citra asli dimuat (RGB): ' file]);
        show_original(d);
    end
    
    function btn_load_reference(~, ~)
        [file, path] = uigetfile({'*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff', ...
                                   'Image Files'}, 'Pilih Citra Referensi');
        if isequal(file, 0), return; end
        
        d = guidata(fig);
        img = imread(fullfile(path, file));
        d.img_reference = ensure_rgb(img);
        guidata(fig, d);
        
        set(status_label, 'String', ['Citra referensi dimuat (RGB): ' file]);
        show_with_reference(d);
    end
    
    function btn_equalization(~, ~)
        d = guidata(fig);
        if isempty(d.img_original)
            msgbox('Silakan load citra asli terlebih dahulu!', 'Peringatan', 'warn');
            return;
        end
        
        % Equalize per channel
        result = uint8(zeros(size(d.img_original)));
        for ch = 1:3
            result(:,:,ch) = eq_channel(d.img_original(:,:,ch));
        end
        d.img_equalized = result;
        guidata(fig, d);
        
        set(status_label, 'String', 'Histogram Equalization selesai (RGB).');
        show_equalization(d);
    end
    
    function btn_specification(~, ~)
        d = guidata(fig);
        if isempty(d.img_original)
            msgbox('Silakan load citra asli terlebih dahulu!', 'Peringatan', 'warn');
            return;
        end
        if isempty(d.img_reference)
            msgbox('Silakan load citra referensi terlebih dahulu!', 'Peringatan', 'warn');
            return;
        end
        
        % Specification per channel
        result = uint8(zeros(size(d.img_original)));
        for ch = 1:3
            result(:,:,ch) = spec_channel(d.img_original(:,:,ch), d.img_reference(:,:,ch));
        end
        d.img_specified = result;
        guidata(fig, d);
        
        set(status_label, 'String', 'Histogram Specification selesai (RGB).');
        show_specification(d);
    end
    
    function btn_save(~, ~)
        d = guidata(fig);
        if ~isempty(d.img_specified)
            img_out = d.img_specified;
        elseif ~isempty(d.img_equalized)
            img_out = d.img_equalized;
        else
            msgbox('Belum ada hasil untuk disimpan!', 'Peringatan', 'warn');
            return;
        end
        [file, path] = uiputfile({'*.png','PNG';'*.jpg','JPEG';'*.bmp','BMP'}, 'Simpan Hasil');
        if ~isequal(file, 0)
            imwrite(img_out, fullfile(path, file));
            set(status_label, 'String', ['Hasil disimpan: ' fullfile(path, file)]);
        end
    end
    
    function btn_reset(~, ~)
        d.img_original = [];
        d.img_reference = [];
        d.img_equalized = [];
        d.img_specified = [];
        guidata(fig, d);
        allAxes = findall(fig, 'Type', 'axes');
        delete(allAxes);
        set(status_label, 'String', 'Siap. Silakan load citra asli untuk memulai.');
    end
    
    % ===== DISPLAY =====
    
    function show_original(d)
        allAxes = findall(fig, 'Type', 'axes');
        delete(allAxes);
        
        ax1 = axes('Parent', fig, 'Position', [0.05 0.12 0.42 0.65]);
        imshow(d.img_original, 'Parent', ax1);
        title(ax1, 'Citra Asli (RGB)', 'Color', lbl_fg, 'FontSize', 12, 'FontWeight', 'bold');
        
        ax2 = axes('Parent', fig, 'Position', [0.55 0.12 0.42 0.65]);
        plot_rgb_hist(ax2, d.img_original, 'Histogram Citra Asli (RGB)');
    end
    
    function show_with_reference(d)
        if isempty(d.img_original), return; end
        allAxes = findall(fig, 'Type', 'axes');
        delete(allAxes);
        
        ax1 = axes('Parent', fig, 'Position', [0.03 0.45 0.22 0.40]);
        imshow(d.img_original, 'Parent', ax1);
        title(ax1, 'Citra Asli', 'Color', lbl_fg, 'FontSize', 10);
        
        ax2 = axes('Parent', fig, 'Position', [0.28 0.45 0.22 0.40]);
        plot_rgb_hist(ax2, d.img_original, 'Histogram Asli');
        
        ax3 = axes('Parent', fig, 'Position', [0.53 0.45 0.22 0.40]);
        imshow(d.img_reference, 'Parent', ax3);
        title(ax3, 'Citra Referensi', 'Color', lbl_fg, 'FontSize', 10);
        
        ax4 = axes('Parent', fig, 'Position', [0.78 0.45 0.20 0.40]);
        plot_rgb_hist(ax4, d.img_reference, 'Histogram Referensi');
    end
    
    function show_equalization(d)
        allAxes = findall(fig, 'Type', 'axes');
        delete(allAxes);
        
        ax1 = axes('Parent', fig, 'Position', [0.03 0.45 0.22 0.40]);
        imshow(d.img_original, 'Parent', ax1);
        title(ax1, 'Citra Asli', 'Color', lbl_fg, 'FontSize', 10);
        
        ax2 = axes('Parent', fig, 'Position', [0.28 0.45 0.22 0.40]);
        plot_rgb_hist(ax2, d.img_original, 'Histogram Asli');
        
        ax3 = axes('Parent', fig, 'Position', [0.53 0.45 0.22 0.40]);
        imshow(d.img_equalized, 'Parent', ax3);
        title(ax3, 'Hasil Equalization', 'Color', lbl_fg, 'FontSize', 10);
        
        ax4 = axes('Parent', fig, 'Position', [0.78 0.45 0.20 0.40]);
        plot_rgb_hist(ax4, d.img_equalized, 'Histogram Equalized');
    end
    
    function show_specification(d)
        allAxes = findall(fig, 'Type', 'axes');
        delete(allAxes);
        
        ax1 = axes('Parent', fig, 'Position', [0.03 0.50 0.30 0.38]);
        imshow(d.img_original, 'Parent', ax1);
        title(ax1, 'Citra Asli', 'Color', lbl_fg, 'FontSize', 10);
        
        ax2 = axes('Parent', fig, 'Position', [0.36 0.50 0.30 0.38]);
        imshow(d.img_reference, 'Parent', ax2);
        title(ax2, 'Citra Referensi', 'Color', lbl_fg, 'FontSize', 10);
        
        ax3 = axes('Parent', fig, 'Position', [0.69 0.50 0.30 0.38]);
        imshow(d.img_specified, 'Parent', ax3);
        title(ax3, 'Hasil Specification', 'Color', lbl_fg, 'FontSize', 10);
        
        ax4 = axes('Parent', fig, 'Position', [0.03 0.06 0.30 0.35]);
        plot_rgb_hist(ax4, d.img_original, 'Histogram Asli');
        
        ax5 = axes('Parent', fig, 'Position', [0.36 0.06 0.30 0.35]);
        plot_rgb_hist(ax5, d.img_reference, 'Histogram Referensi');
        
        ax6 = axes('Parent', fig, 'Position', [0.69 0.06 0.30 0.35]);
        plot_rgb_hist(ax6, d.img_specified, 'Histogram Hasil');
    end

end
