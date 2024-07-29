import React from 'react';
import { Edit2, Check, Save } from 'lucide-react';

interface GameStateTabProps {
    gameInfo: { [key: string]: string };
    editingGameInfoField: string | null;
    editedGameInfoContent: string;
    handleEditGameInfoField: (field: string) => void;
    handleSaveEditedGameInfoField: (field: string) => void;
    setEditedGameInfoContent: (content: string) => void;
    handleSaveGame: () => void;
}

const GameStateTab: React.FC<GameStateTabProps> = ({
                                                       gameInfo,
                                                       editingGameInfoField,
                                                       editedGameInfoContent,
                                                       handleEditGameInfoField,
                                                       handleSaveEditedGameInfoField,
                                                       setEditedGameInfoContent,
                                                       handleSaveGame,
                                                   }) => {
    return (
        <section className="flex-grow flex flex-col bg-[#0d1117] overflow-hidden relative w-full h-full p-4">
            <div className="max-w-3xl mx-auto w-full">
                <h2 className="text-xl font-semibold text-gray-100 mb-4">Game Information</h2>
                <div className="space-y-4">
                    {Object.entries(gameInfo).map(([key, value]) => (
                        <div key={key} className="bg-[#1c2128] p-4 rounded-lg">
                            <div className="flex justify-between items-center mb-2">
                                <h3 className="font-semibold text-gray-200">{key}</h3>
                                {editingGameInfoField !== key && (
                                    <button
                                        onClick={() => handleEditGameInfoField(key)}
                                        className="text-gray-400 hover:text-gray-200 transition-colors"
                                        aria-label={`Edit ${key}`}
                                    >
                                        <Edit2 size={16}/>
                                    </button>
                                )}
                            </div>
                            {editingGameInfoField === key ? (
                                <div className="flex items-center mt-2">
                  <textarea
                      value={editedGameInfoContent}
                      onChange={(e) => setEditedGameInfoContent(e.target.value)}
                      className="flex-grow bg-[#0d1117] p-2 rounded-lg text-gray-200 resize-none"
                      rows={5}
                  />
                                    <button
                                        onClick={() => handleSaveEditedGameInfoField(key)}
                                        className="ml-2 bg-green-500 hover:bg-green-600 text-white p-2 rounded-lg transition-colors"
                                        aria-label={`Save ${key}`}
                                    >
                                        <Check size={16}/>
                                    </button>
                                </div>
                            ) : (
                                <pre className="text-gray-400 whitespace-pre-wrap break-words">{value}</pre>
                            )}
                        </div>
                    ))}
                </div>
                <div className="mt-6">
                    <button
                        onClick={handleSaveGame}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded transition-colors flex items-center justify-center"
                    >
                        <Save size={18} className="mr-2"/>
                        Save Game
                    </button>
                </div>
            </div>
        </section>
    );
};

export default GameStateTab;