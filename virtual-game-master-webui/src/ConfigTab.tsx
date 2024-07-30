import React, { useState, useEffect } from 'react';
import {FolderPlus, Save} from 'lucide-react';

interface ConfigTabProps {
    config: {
        GAME_SAVE_FOLDER: string;
        INITIAL_GAME_STATE: string;
        TEMPERATURE: number;
        TOP_P: number;
        TOP_K: number;
        MIN_P: number;
        TFS_Z: number;
    };
    onSaveConfig: (newConfig: any) => void;
    onUpdateGameConfig: (newConfig: any) => void;
}

const ConfigTab: React.FC<ConfigTabProps> = ({ config, onSaveConfig, onUpdateGameConfig }) => {
    const [editedConfig, setEditedConfig] = useState(config);
    const [folders, setFolders] = useState<string[]>([]);
    const [gameStarters, setGameStarters] = useState<string[]>([]);
    const [activeFolder, setActiveFolder] = useState<string>('');
    const [activeGame, setActiveGame] = useState<string>('');
    const [newFolderName, setNewFolderName] = useState<string>('');
    const [showNewFolderInput, setShowNewFolderInput] = useState<boolean>(false);
    useEffect(() => {
        fetchFolders();
        fetchGameStarters();
    }, []);

    const fetchFolders = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/get_chat_history_folders');
            const data = await response.json();
            console.log(data.active)
            setActiveFolder(data.active)
            setFolders(data.folders);
        } catch (error) {
            console.error('Failed to fetch folders:', error);
        }
    };

    const fetchGameStarters = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/get_game_starters');
            const data = await response.json();
            console.log(data.active)
            setActiveGame(data.active)
            setGameStarters(data.game_starters);
        } catch (error) {
            console.error('Failed to fetch game starters:', error);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setEditedConfig({ ...editedConfig, [name]: value });
    };

    const handleSave = () => {
        onSaveConfig(editedConfig);
    };

    const handleGameConfigUpdate = () => {
        onUpdateGameConfig(editedConfig)
    };

    const handleCreateNewFolder = async () => {
        if (newFolderName.trim() === '') {
            alert('Please enter a valid folder name');
            return;
        }

        try {
            const response = await fetch('http://localhost:8000/api/create_game_save_folder/' + newFolderName, {
                method: 'POST'
            });

            if (response.ok) {
                alert('New game save folder created successfully');
                setNewFolderName('');
                setShowNewFolderInput(false);
                await fetchFolders(); // Refresh the folder list
            } else {
                alert('Failed to create new game save folder');
            }
        } catch (error) {
            console.error('Error creating new game save folder:', error);
            alert('An error occurred while creating the new game save folder');
        }
    };
    return (
        <section className="flex-grow flex flex-col bg-[#0d1117] overflow-hidden relative w-full h-full p-4">
            <div className="max-w-3xl mx-auto w-full">
                <h2 className="text-xl font-semibold text-gray-100 mb-4">Configuration</h2>
                <div className="space-y-4">
                    <div className="bg-[#1c2128] p-4 rounded-lg">
                        <h3 className="font-semibold text-gray-200 mb-2">Model Sampling Parameters</h3>
                        <div className="grid grid-cols-2 gap-4">
                            {['TEMPERATURE', 'TOP_P', 'TOP_K', 'MIN_P', 'TFS_Z'].map((param) => (
                                <div key={param}>
                                    <label htmlFor={param} className="block text-sm font-medium text-gray-400">
                                        {param}
                                    </label>
                                    <input
                                        type="number"
                                        id={param}
                                        name={param}
                                        value={editedConfig[param as keyof typeof editedConfig]}
                                        onChange={handleInputChange}
                                        className="mt-1 block w-full bg-[#0d1117] border border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="bg-[#1c2128] p-4 rounded-lg">
                        <h3 className="font-semibold text-gray-200 mb-2">Game Settings</h3>
                        <div className="space-y-4">
                            <div>
                                <label htmlFor="GAME_SAVE_FOLDER" className="block text-sm font-medium text-gray-400">
                                    Game Save Folder
                                </label>
                                <div className="flex items-center space-x-2">
                                    <select
                                        id="GAME_SAVE_FOLDER"
                                        name="GAME_SAVE_FOLDER"
                                        value={activeFolder}
                                        onChange={handleInputChange}
                                        className="mt-1 block w-full bg-[#0d1117] border border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                    >
                                        {folders.map((folder) => (
                                            <option key={folder} value={folder}>
                                                {folder}
                                            </option>
                                        ))}
                                    </select>
                                    <button
                                        onClick={() => setShowNewFolderInput(!showNewFolderInput)}
                                        className="mt-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-3 rounded transition-colors flex items-center justify-center"
                                    >
                                        <FolderPlus size={18} />
                                    </button>
                                </div>
                            </div>
                            {showNewFolderInput && (
                                <div className="flex items-center space-x-2">
                                    <input
                                        type="text"
                                        value={newFolderName}
                                        onChange={(e) => setNewFolderName(e.target.value)}
                                        placeholder="New folder name"
                                        className="mt-1 block w-full bg-[#0d1117] border border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                    />
                                    <button
                                        onClick={handleCreateNewFolder}
                                        className="mt-1 bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-3 rounded transition-colors"
                                    >
                                        Create
                                    </button>
                                </div>
                            )}

                            <div>
                                <label htmlFor="INITIAL_GAME_STATE" className="block text-sm font-medium text-gray-400">
                                    Initial Game State File
                                </label>
                                <select
                                    id="INITIAL_GAME_STATE"
                                    name="INITIAL_GAME_STATE"
                                    value={activeGame}
                                    onChange={handleInputChange}
                                    className="mt-1 block w-full bg-[#0d1117] border border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                >
                                    {gameStarters.map((starter) => (
                                        <option key={starter} value={starter}>
                                            {starter}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="mt-6">
                    <button
                        onClick={handleGameConfigUpdate}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded transition-colors flex items-center justify-center"
                    >
                        <Save size={18} className="mr-2"/>
                        Update Game
                    </button>
                </div>
                <div className="mt-6">
                    <button
                        onClick={handleSave}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded transition-colors flex items-center justify-center"
                    >
                        <Save size={18} className="mr-2"/>
                        Save Configuration to .env file
                    </button>
                </div>
            </div>
        </section>
    );
};

export default ConfigTab;