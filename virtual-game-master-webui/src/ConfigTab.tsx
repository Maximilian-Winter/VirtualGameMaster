import React, { useState, useEffect } from 'react';
import { Save } from 'lucide-react';

interface ConfigTabProps {
    config: Record<string, any>;
    onSaveConfig: (newConfig: Record<string, any>) => void;
}

const ConfigTab: React.FC<ConfigTabProps> = ({ config, onSaveConfig }) => {
    const [editedConfig, setEditedConfig] = useState<Record<string, any>>({});

    useEffect(() => {
        setEditedConfig(config);
    }, [config]);

    const handleInputChange = (key: string, value: string) => {
        setEditedConfig((prev) => ({ ...prev, [key]: value }));
    };

    const handleSaveConfig = () => {
        onSaveConfig(editedConfig);
    };

    return (
        <section className="flex-grow flex flex-col bg-[#0d1117] overflow-hidden relative w-full h-full p-4">
            <div className="max-w-3xl mx-auto w-full">
                <h2 className="text-xl font-semibold text-gray-100 mb-4">Configuration</h2>
                <div className="space-y-4">
                    {Object.entries(editedConfig).map(([key, value]) => (
                        <div key={key} className="bg-[#1c2128] p-4 rounded-lg">
                            <label htmlFor={key} className="block text-sm font-medium text-gray-200 mb-2">
                                {key}
                            </label>
                            <input
                                type="text"
                                id={key}
                                value={value as string}
                                onChange={(e) => handleInputChange(key, e.target.value)}
                                className="w-full bg-[#0d1117] p-2 rounded-lg text-gray-200 border border-gray-700"
                            />
                        </div>
                    ))}
                </div>
                <div className="mt-6">
                    <button
                        onClick={handleSaveConfig}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded transition-colors flex items-center justify-center"
                    >
                        <Save size={18} className="mr-2" />
                        Save Configuration
                    </button>
                </div>
            </div>
        </section>
    );
};

export default ConfigTab;