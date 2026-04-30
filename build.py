import os
import re
import html
import shutil

def parse_readme(file_path="README.md"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    tools = []

    for line in content.splitlines():
        line = line.strip()
        if not (line.startswith("[") or line.startswith("- [")):
            continue

        links_matches = list(re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line))

        if not links_matches:
            continue

        name = links_matches[0].group(1)
        url = links_matches[0].group(2)

        github_url = None
        svg_url = None
        mcp_url = None
        last_match = links_matches[0]

        for i in range(1, len(links_matches)):
            link_text = links_matches[i].group(1).lower()
            if link_text == "github":
                github_url = links_matches[i].group(2)
                last_match = links_matches[i]
            elif link_text == "svg":
                svg_url = links_matches[i].group(2)
                last_match = links_matches[i]
            elif link_text == "mcp":
                mcp_url = links_matches[i].group(2)
                last_match = links_matches[i]

        desc_start_colon = line.find(":", last_match.end())
        desc_start_dash = line.find(" - ", last_match.end())

        description = ""
        if desc_start_colon != -1:
            description = line[desc_start_colon + 1:].strip()
        elif desc_start_dash != -1:
            description = line[desc_start_dash + 3:].strip()

        tools.append({
            "name": name,
            "url": url,
            "github_url": github_url,
            "svg_url": svg_url,
            "mcp_url": mcp_url,
            "description": description
        })

    return tools

def generate_html(tools, dest_dir="dst"):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    if os.path.exists("icons"):
        dst_icons = os.path.join(dest_dir, "icons")
        if os.path.exists(dst_icons):
            shutil.rmtree(dst_icons)
        shutil.copytree("icons", dst_icons)

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Build for Agents</title>
    <!-- Tailwind CSS v4 CDN -->
    <script src="https://unpkg.com/@tailwindcss/browser@4"></script>
    <style>
        /* Custom styles if any */
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
    </style>
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen">
    <div class="max-w-5xl mx-auto px-4 py-12">
        <header class="mb-16 text-center">
            <h1 class="text-5xl font-extrabold text-gray-900 mb-6 tracking-tight">Build for Agents</h1>
            <p class="text-xl text-gray-600 max-w-2xl mx-auto">A curated list of tools and services that are specifically built for agents</p>
        </header>

        <div class="mb-10">
            <div class="relative max-w-2xl mx-auto">
                <input type="text" id="searchInput"
                       class="w-full pl-14 pr-4 py-4 rounded-2xl border-0 ring-1 ring-gray-200 shadow-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all text-lg bg-white"
                       placeholder="Search tools...">
                <svg class="absolute left-5 top-4.5 h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
            </div>
        </div>

        <div id="toolsList" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {cards}
        </div>

        <div id="noResults" class="hidden text-center py-16 text-gray-500 text-lg">
            <div class="mb-4">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            </div>
            No tools found matching your search.
        </div>

        <footer class="mt-20 pt-8 border-t border-gray-200 text-center text-gray-500 text-sm pb-8">
            <p>Open source repository. Contributions welcome on <a href="https://github.com/agentrq/buildforagents" class="text-blue-600 hover:text-blue-800 transition-colors font-medium">GitHub</a>.</p>
        </footer>
    </div>

    <script>
        function copyMcpUrl(event, button, url) {
            event.preventDefault();
            event.stopPropagation();
            navigator.clipboard.writeText(url).then(() => {
                const container = button.closest('.mcp-container');
                const mcpSvg = button.querySelector('.mcp-svg');
                const checkSvg = button.querySelector('.check-svg');
                const copySvg = button.querySelector('.copy-svg');
                const tooltip = container.querySelector('.mcp-tooltip');

                // Show check mark
                mcpSvg.classList.add('hidden');
                copySvg.classList.add('hidden');
                checkSvg.classList.remove('hidden');

                // Change tooltip text
                const originalHtml = tooltip.innerHTML;
                tooltip.innerHTML = '<span>Copied!</span><div class="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45"></div>';

                setTimeout(() => {
                    checkSvg.classList.add('hidden');
                    tooltip.innerHTML = originalHtml;

                    if (!tooltip.classList.contains('hidden')) {
                        copySvg.classList.remove('hidden');
                    } else {
                        mcpSvg.classList.remove('hidden');
                    }
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        }

        document.addEventListener('DOMContentLoaded', () => {
            // Setup MCP tooltips hover behavior
            document.querySelectorAll('.mcp-container').forEach(container => {
                const btn = container.querySelector('.mcp-btn');
                const tooltip = container.querySelector('.mcp-tooltip');
                const copySvg = container.querySelector('.copy-svg');
                const mcpSvg = container.querySelector('.mcp-svg');

                btn.addEventListener('mouseenter', () => {
                    tooltip.classList.remove('hidden');
                    if (container.querySelector('.check-svg').classList.contains('hidden')) {
                        mcpSvg.classList.add('hidden');
                        copySvg.classList.remove('hidden');
                    }
                });

                btn.addEventListener('mouseleave', () => {
                    tooltip.classList.add('hidden');
                    // Only restore MCP svg if we aren't showing the check mark
                    if (container.querySelector('.check-svg').classList.contains('hidden')) {
                        mcpSvg.classList.remove('hidden');
                        copySvg.classList.add('hidden');
                    }
                });
            });

            const searchInput = document.getElementById('searchInput');
            const tools = document.querySelectorAll('.tool-card');
            const noResults = document.getElementById('noResults');

            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                let hasVisibleCards = false;

                tools.forEach(tool => {
                    const searchData = tool.getAttribute('data-search');
                    if (searchData.includes(searchTerm)) {
                        tool.style.display = '';
                        hasVisibleCards = true;
                    } else {
                        tool.style.display = 'none';
                    }
                });

                if (hasVisibleCards) {
                    noResults.classList.add('hidden');
                } else {
                    noResults.classList.remove('hidden');
                }
            });
        });
    </script>
</body>
</html>
"""

    cards_html = []
    for tool in tools:
        search_data = html.escape(f"{tool['name']} {tool['description']}").lower()

        icons_container = []
        if tool.get('mcp_url'):
            escaped_mcp = html.escape(tool['mcp_url'])
            mcp_icon = f"""
                <div class="relative inline-block mcp-container">
                    <button type="button" onclick="copyMcpUrl(event, this, '{escaped_mcp}')" class="text-gray-400 hover:text-gray-900 transition-colors bg-gray-50 hover:bg-gray-100 p-2 rounded-full cursor-pointer mcp-btn" title="Copy MCP URL">
                        <svg class="w-5 h-5 mcp-svg" viewBox="0 0 180 180" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                            <g clip-path="url(#clip0_19_13)">
                                <path d="M18 84.8528L85.8822 16.9706C95.2548 7.59798 110.451 7.59798 119.823 16.9706V16.9706C129.196 26.3431 129.196 41.5391 119.823 50.9117L68.5581 102.177" stroke="currentColor" stroke-width="12" stroke-linecap="round"/>
                                <path d="M69.2652 101.47L119.823 50.9117C129.196 41.5391 144.392 41.5391 153.765 50.9117L154.118 51.2652C163.491 60.6378 163.491 75.8338 154.118 85.2063L92.7248 146.6C89.6006 149.724 89.6006 154.789 92.7248 157.913L105.331 170.52" stroke="currentColor" stroke-width="12" stroke-linecap="round"/>
                                <path d="M102.853 33.9411L52.6482 84.1457C43.2756 93.5183 43.2756 108.714 52.6482 118.087V118.087C62.0208 127.459 77.2167 127.459 86.5893 118.087L136.794 67.8822" stroke="currentColor" stroke-width="12" stroke-linecap="round"/>
                            </g>
                            <defs>
                                <clipPath id="clip0_19_13">
                                    <rect width="180" height="180" fill="white"/>
                                </clipPath>
                            </defs>
                        </svg>
                        <svg class="w-5 h-5 copy-svg hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path>
                        </svg>
                        <svg class="w-5 h-5 check-svg hidden text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                    </button>
                    <div class="mcp-tooltip hidden absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap shadow-lg flex items-center gap-2 max-w-xs z-50">
                        <span class="truncate">{escaped_mcp}</span>
                        <div class="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45"></div>
                    </div>
                </div>
            """
            icons_container.append(mcp_icon)

        if tool['github_url']:
            github_icon = f"""
                <a href="{html.escape(tool['github_url'])}" target="_blank" rel="noopener noreferrer" class="text-gray-400 hover:text-gray-900 transition-colors bg-gray-50 hover:bg-gray-100 p-2 rounded-full" title="View on GitHub">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
                    </svg>
                </a>
            """
            icons_container.append(github_icon)

        right_icons_html = "".join(icons_container)

        icon_html = f"""
            <div class="w-12 h-12 rounded-xl bg-gray-50 flex items-center justify-center flex-shrink-0 border border-gray-100 overflow-hidden mr-4">
                <span class="text-xl font-bold text-gray-400">{html.escape(tool['name'][0].upper())}</span>
            </div>
        """
        if tool.get('svg_url'):
            icon_html = f"""
            <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 mr-4">
                <img src="{html.escape(tool['svg_url'])}" alt="{html.escape(tool['name'])} icon" class="w-full h-full object-contain">
            </div>
            """

        card = f"""
            <div class="tool-card relative bg-white rounded-2xl shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100 flex flex-col group" data-search="{search_data}">
                <div class="p-6 flex-grow">
                    <div class="flex justify-between items-start mb-4">
                        <div class="flex items-center">
                            {icon_html}
                            <h2 class="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                                <a href="{html.escape(tool['url'])}" target="_blank" rel="noopener noreferrer" class="focus:outline-none">
                                    <span class="absolute inset-0" aria-hidden="true"></span>
                                    {html.escape(tool['name'])}
                                </a>
                            </h2>
                        </div>
                        <div class="relative z-10 flex-shrink-0 ml-2 flex items-center gap-1">
                            {right_icons_html}
                        </div>
                    </div>
                    <p class="text-gray-600 leading-relaxed text-sm">
                        {html.escape(tool['description'])}
                    </p>
                </div>
                <div class="px-6 py-4 bg-gray-50 rounded-b-2xl border-t border-gray-50 flex items-center justify-between group-hover:bg-blue-50 transition-colors relative z-10">
                    <a href="{html.escape(tool['url'])}" target="_blank" rel="noopener noreferrer" class="text-blue-600 font-medium text-sm hover:text-blue-800 flex items-center w-full">
                        Visit Website
                        <svg class="w-4 h-4 ml-1.5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                        </svg>
                    </a>
                </div>
            </div>
        """
        cards_html.append(card)

    final_html = html_template.replace("{cards}", "\n".join(cards_html))

    with open(os.path.join(dest_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    tools = parse_readme()
    generate_html(tools)
    print(f"Generated index.html in dst/ directory with {len(tools)} tools.")
